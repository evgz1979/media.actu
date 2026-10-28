"""SMB discovery using macOS tools. No mounting, password prompts or file writes."""
from __future__ import annotations

import json
import re
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit

from media_manager.storage import now, volume_key


class NetworkError(RuntimeError):
    pass


def validate_host(host: str) -> str:
    host = host.rstrip('.').lower()
    if len(host) > 253 or not re.fullmatch(r'[a-z0-9_](?:[a-z0-9_.()-]*[a-z0-9_])?', host):
        raise NetworkError('Некорректный адрес NAS')
    return host


def validate_share(name: str) -> str:
    if not name or name in {'.', '..'} or len(name) > 255 or any(ord(c) < 32 or c in '/\\' for c in name):
        raise NetworkError('Некорректное имя сетевого ресурса')
    return name


def parse_browse(output: str) -> list[dict]:
    instances = {}
    for line in output.splitlines():
        match = re.match(r'^\S+\s+(Add|Rmv)\s+\d+\s+(\d+)\s+(local\.)\s+_smb\._tcp\.?\s+(.+?)\s*$', line)
        if not match:
            continue
        action, interface, domain, name = match.groups()
        key = (name, domain, interface)
        if action == 'Add':
            instances[key] = {'name': name, 'domain': domain}
        else:
            instances.pop(key, None)
    unique = {(v['name'], v['domain']): v for v in instances.values()}
    return list(unique.values())


def parse_resolve(output: str) -> tuple[str, int]:
    match = re.search(r'can be reached at ([^\s:]+):(\d+)\s+\(interface', output)
    if not match:
        raise NetworkError('Сервер объявлен в сети, но его адрес пока не получен')
    host, port = match.groups()
    if int(port) != 445:
        raise NetworkError('В этой версии поддерживается стандартный порт SMB 445')
    return validate_host(host), int(port)


def parse_shares(output: str) -> list[dict]:
    shares = []
    in_table = False
    completed = False
    for line in output.splitlines():
        if line.startswith('---'):
            in_table = True
            continue
        if not in_table or not line.strip():
            continue
        if re.fullmatch(r'\d+ shares? listed', line.strip()):
            completed = True
            continue
        match = re.match(r'^(.*?)\s{2,}(Disk|Pipe|Printer|Comm|Unknown)\s*(.*)$', line)
        if not match:
            raise NetworkError('Не удалось разобрать список ресурсов NAS')
        name, kind, comment = match.groups()
        if kind == 'Disk':
            shares.append({'name': validate_share(name), 'comment': comment.strip()})
    if not in_table or not completed:
        raise NetworkError('NAS не вернул полный список ресурсов')
    return shares


def run(command: list[str], timeout: int) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired as error:
        raise NetworkError('NAS не ответил вовремя; сохранённые сведения оставлены') from error
    except OSError as error:
        raise NetworkError('Не удалось запустить штатное средство macOS для поиска NAS') from error
    if result.returncode:
        # Never expose connection diagnostics which could contain account details.
        raise NetworkError('Не удалось получить сведения NAS без запроса пароля. Подключись к нему через Finder на M4 и повтори.')
    return result.stdout


def discover_servers() -> list[dict]:
    output = run(['/usr/bin/dns-sd', '-t', '4', '-B', '_smb._tcp', 'local.'], 7)
    instances = parse_browse(output)
    if len(instances) > 32:
        raise NetworkError('Найдено больше 32 SMB-серверов; поиск нужно сузить')

    def resolve(instance):
        if instance['name'].startswith('-') or any(ord(c) < 32 for c in instance['name']):
            return None
        try:
            output = run(['/usr/bin/dns-sd', '-t', '2', '-L', instance['name'], '_smb._tcp', instance['domain']], 5)
            host, port = parse_resolve(output)
            alias = f"{instance['name']}._smb._tcp.{instance['domain']}".rstrip('.').lower()
            return {'id': volume_key(f'nas:{host}:{port}'), 'name': instance['name'], 'host': host, 'port': port, 'aliases': [host, alias]}
        except NetworkError:
            return None

    servers = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for server in pool.map(resolve, instances):
            if server is None:
                continue
            previous = servers.get(server['id'])
            if previous:
                previous['aliases'] = sorted(set(previous['aliases'] + server['aliases']))
                previous['name'] = min(previous['name'], server['name'], key=len)
            else:
                servers[server['id']] = server
    if instances and not servers:
        raise NetworkError('Найдены объявления SMB, но адреса серверов не получены. Попробуй поиск ещё раз.')
    return list(servers.values())


def list_server_shares(server: dict) -> list[dict]:
    host = validate_host(server['host'])
    return parse_shares(run(['/usr/bin/smbutil', 'view', '-N', f'//{host}'], 12))


class NetworkCatalog:
    def __init__(self, storage, discover=discover_servers, list_shares=list_server_shares):
        self.storage = storage
        self.discover = discover
        self.list_shares = list_shares
        self._scan_lock = threading.Lock()
        self._shares_lock = threading.Lock()
        with storage.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS network_servers (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, host TEXT NOT NULL,
                    port INTEGER NOT NULL, aliases TEXT NOT NULL, last_seen TEXT NOT NULL,
                    discovered INTEGER NOT NULL DEFAULT 1, shares_at TEXT, error TEXT
                );
                CREATE TABLE IF NOT EXISTS network_shares (
                    server_id TEXT NOT NULL, name TEXT NOT NULL, comment TEXT NOT NULL,
                    last_seen TEXT NOT NULL, present INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY(server_id, name)
                );
            ''')

    def servers(self) -> dict:
        with self.storage.connect() as db:
            rows = [dict(r) for r in db.execute('SELECT * FROM network_servers ORDER BY name COLLATE NOCASE')]
        for row in rows:
            row['aliases'] = json.loads(row['aliases'])
        return {'servers': rows}

    def server(self, server_id: str) -> dict:
        server = next((r for r in self.servers()['servers'] if r['id'] == server_id), None)
        if server is None:
            raise KeyError('NAS не найден')
        return server

    def scan(self) -> dict:
        if not self._scan_lock.acquire(blocking=False):
            return {**self.servers(), 'error': 'Поиск NAS уже выполняется', 'scanning': True}
        try:
            try:
                discovered = self.discover()
            except NetworkError as error:
                return {**self.servers(), 'error': str(error)}
            timestamp = now()
            with self.storage.connect() as db:
                db.execute('UPDATE network_servers SET discovered=0')
                for server in discovered:
                    previous = db.execute('SELECT aliases FROM network_servers WHERE id=?', (server['id'],)).fetchone()
                    aliases = sorted(set(server['aliases'] + (json.loads(previous['aliases']) if previous else [])))
                    db.execute('''
                        INSERT INTO network_servers (id,name,host,port,aliases,last_seen,discovered)
                        VALUES (?,?,?,?,?,?,1) ON CONFLICT(id) DO UPDATE SET name=excluded.name,
                        host=excluded.host, port=excluded.port, aliases=excluded.aliases,
                        last_seen=excluded.last_seen, discovered=1
                    ''', (server['id'], server['name'], server['host'], server['port'], json.dumps(aliases), timestamp))
            return {**self.servers(), 'error': None}
        finally:
            self._scan_lock.release()

    def shares(self, server_id: str, refresh: bool = False) -> dict:
        server = self.server(server_id)
        error = server['error']
        if refresh:
            with self._shares_lock:
                try:
                    shares = self.list_shares(server)
                    timestamp = now()
                    with self.storage.connect() as db:
                        db.execute('UPDATE network_shares SET present=0 WHERE server_id=?', (server_id,))
                        for share in shares:
                            db.execute('''
                                INSERT INTO network_shares VALUES (?,?,?,?,1)
                                ON CONFLICT(server_id,name) DO UPDATE SET comment=excluded.comment,
                                last_seen=excluded.last_seen, present=1
                            ''', (server_id, share['name'], share['comment'], timestamp))
                        db.execute('UPDATE network_servers SET shares_at=?,error=NULL WHERE id=?', (timestamp, server_id))
                    error = None
                except NetworkError as failure:
                    error = str(failure)
                    with self.storage.connect() as db:
                        db.execute('UPDATE network_servers SET error=? WHERE id=?', (error, server_id))
            server = self.server(server_id)
        with self.storage.connect() as db:
            rows = [dict(r) for r in db.execute('SELECT * FROM network_shares WHERE server_id=? ORDER BY name COLLATE NOCASE', (server_id,))]
        for row in rows:
            known = self.storage.find_network_volume(server['aliases'], row['name'])
            row['volume_id'] = known['id'] if known else None
        return {'server': server, 'shares': rows, 'error': error, 'cached': not refresh or bool(error)}

    def remember(self, server_id: str, name: str) -> dict:
        server = self.server(server_id)
        name = validate_share(name)
        if not any(r['name'] == name for r in self.shares(server_id)['shares']):
            raise KeyError('Ресурс не найден в сохранённом списке NAS')
        return self.storage.remember_network_volume(server['host'], server['aliases'], name)

    def open_in_finder(self, volume_id: str) -> dict:
        volume = self.storage.get_volume(volume_id)
        url = volume.get('network_url')
        parts = urlsplit(url or '')
        if parts.scheme != 'smb' or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment:
            raise NetworkError('У этого тома нет адреса SMB. Сначала выбери его в поиске NAS.')
        validate_host(parts.hostname)
        try:
            if parts.port not in (None, 445):
                raise ValueError('port')
        except ValueError as error:
            raise NetworkError('Некорректный порт SMB') from error
        try:
            subprocess.run(['/usr/bin/open', url], check=True, timeout=8, stdin=subprocess.DEVNULL, capture_output=True)
        except (OSError, subprocess.SubprocessError) as error:
            raise NetworkError('Не удалось открыть подключение в Finder на M4') from error
        return {'url': url, 'status': 'finder_opened'}
