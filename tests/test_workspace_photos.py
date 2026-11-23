from contextlib import nullcontext
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from copy_panels import copy_heading
from paired_workspace_ui import PairedWorkspace
from photo_libraries_ui import PhotoLibrariesUI
from workspace_state import normalize_state
from workspace_ui import BrowserPane, StorageWorkspace


#: Проверяет общие пары для Photos и iCloud поверх сохранённых привязок.
#: Подменяет просмотр деревьев и Core, сохраняя настоящий контроллер пары.
class WorkspacePhotosTests(unittest.IsolatedAsyncioTestCase):
    #: Собирает тестовые панели и рабочее пространство без интерфейса NiceGUI.
    #: Использует реальные методы открытия и связывания панелей.
    def workspace(self):
        ws = StorageWorkspace.__new__(StorageWorkspace)
        ws.client = nullcontext()
        ws.panes = [SimpleNamespace(view_mode='tree', set_mode=AsyncMock(), show_volume=AsyncMock(),
                                    focus_tree=Mock(), save_browse_state=Mock(), hidden=SimpleNamespace(value=False))
                    for _ in range(2)]
        ws.pair = PairedWorkspace(ws)
        ws.pair.render_rail = Mock()
        ws.report = None
        ws.volumes = []
        ws.active_index = 1
        ws.set_active = Mock(side_effect=lambda i: setattr(ws, 'active_index', i))
        ws.open_volume = AsyncMock()
        ws.update_scopes = Mock()
        ws.request = AsyncMock()
        ws.photo_libraries = PhotoLibrariesUI(ws)
        return ws

    #: Создаёт минимальную копию с полями ответа Core для обеих служб.
    #: Принимает переопределения привязки и доступности.
    def copy(self, number, disk, path='Archive/Photos', **fields):
        return {**dict(id=f'copy-{number}', number=number, volume_id=disk, volume_name=disk, path=path,
                       availability='online', active=False, state='idle'), **fields}

    #: Проверяет настоящее открытие пары с первой доступной копией Photos.
    #: Подтверждает возврат к двум деревьям из превью.
    async def test_opening_photos_selects_the_first_available_copy_and_restores_the_destination_tree(self):
        ws = self.workspace()
        ws.panes[1].view_mode = 'preview'
        ws.photo_libraries.libraries = [dict(id=5, active=True, copies=[
            self.copy(3, 'later'), self.copy(1, 'old', availability='offline'), self.copy(2, 'disk'),
        ])]
        await ws.photo_libraries.open_copy('photos-5')
        self.assertTrue(ws.pair.active)
        self.assertEqual(ws.pair.copy_id, 'copy-2')
        ws.panes[1].set_mode.assert_awaited_once_with('tree')
        ws.panes[0].show_volume.assert_awaited_once_with('photos-5', '', activate=False)
        ws.panes[1].show_volume.assert_awaited_once_with('disk', 'Archive/Photos', activate=False)
        self.assertEqual(ws.active_index, 0)

    #: Проверяет обычный просмотр медиатеки без сохранённой копии.
    #: Правое дерево при этом не открывается заново.
    async def test_opening_photos_without_copies_uses_only_the_left_tree(self):
        ws = self.workspace()
        ws.photo_libraries.libraries = [dict(id=6, active=True, copies=[])]
        await ws.photo_libraries.open_copy('photos-6')
        ws.open_volume.assert_awaited_once_with('photos-6', 0, path='')
        ws.panes[1].show_volume.assert_not_awaited()

    #: Проверяет восстановление пары с первой сохранённой офлайн-копией iCloud.
    #: Слева должен открыться точный корень привязки.
    async def test_icloud_opens_the_bound_source_path_even_when_all_copies_are_offline(self):
        ws = self.workspace()
        ws.photo_libraries.cloud = dict(volume=dict(id='icloud-drive', availability='online'), copies=[
            self.copy(2, 'other', 'Archive', source_path='', availability='offline'),
            self.copy(1, 'saved', 'Backups', source_path='Документы/Медиа', availability='offline'),
        ])
        await ws.photo_libraries.open_cloud()
        self.assertTrue(ws.pair.active)
        ws.panes[0].show_volume.assert_awaited_once_with('icloud-drive', 'Документы/Медиа', activate=False)
        ws.panes[1].show_volume.assert_awaited_once_with('saved', 'Backups', activate=False)
        self.assertEqual([copy['id'] for copy in ws.pair.group['copies']], ['copy-1'])

    #: Проверяет общий формат заголовков действующей и архивной пар.
    #: Сохраняет ранее показанные роли обычных папок.
    def test_common_heading_preserves_folder_copy_and_history_captions(self):
        self.assertEqual(copy_heading(dict(label='00-main', number=0)), '00-main (источник копирования)')
        self.assertEqual(copy_heading(dict(label='01-copy', number=1), target=True), '01-copy (копия №1)')
        self.assertEqual(copy_heading(dict(label='01-copy', number=1), target=True, historical=True), 'Прежняя 01-copy')

    #: Проверяет открытие звена цепочки с его физическим источником слева.
    #: Сохраняет общий переход по относительным папкам и исходный просмотр для размыкания.
    async def test_opening_a_chained_photos_copy_uses_its_actual_source(self):
        ws = self.workspace()
        ws.photo_libraries.libraries = [dict(id=5, active=True, copies=[
            self.copy(1, 'nvme', 'Photos'), self.copy(2, 'hdd', 'Archive', source_link_id='copy-1'),
        ])]
        await ws.photo_libraries.open_copy('photos-5')
        await ws.pair.navigate_path(0, '2026')
        ws.panes[0].show_volume.assert_awaited_with('photos-5', '2026', activate=False)
        ws.panes[1].show_volume.assert_awaited_with('nvme', 'Photos/2026', activate=False)
        await ws.photo_libraries.open_copy('photos-5', 'copy-2')
        ws.panes[0].show_volume.assert_awaited_with('nvme', 'Photos', activate=False)
        ws.panes[1].show_volume.assert_awaited_with('hdd', 'Archive', activate=False)
        ws.panes[0].save_browse_state.assert_called_once()
        self.assertEqual(ws.pair.scopes['left']['label'], '01-copy')

    #: Проверяет восстановление привязки iCloud без обращения к файловой сверке.
    #: Восстанавливает относительный путь внутри точной облачной папки.
    async def test_icloud_pair_restores_without_using_folder_comparison_api(self):
        ws = self.workspace()
        ws.photo_libraries.cloud = dict(volume=dict(id='icloud-drive', availability='online'),
                                        copies=[self.copy(2, 'disk', 'Backup', source_path='Документы')])
        ws.restore_panes = AsyncMock(return_value=True)
        saved = normalize_state(dict(version=1, active=0, panes=[dict(volume_id=None)] * 2,
                                     pair=dict(virtual_id='icloud-drive', copy_id='copy-2', root='Медиа')))
        self.assertTrue(await ws.restore_workspace(saved))
        self.assertTrue(ws.pair.active)
        self.assertEqual(ws.pair.copy_id, 'copy-2')
        ws.panes[0].show_volume.assert_awaited_with('icloud-drive', 'Документы/Медиа', activate=False)
        ws.panes[1].show_volume.assert_awaited_with('disk', 'Backup/Медиа', activate=False)
        ws.request.assert_not_awaited()

    #: Проверяет, что виртуальные тома используют свой API и игнорируются сверкой имён.
    #: Покрывает режимы дерева и превью.
    async def test_photos_browse_never_uses_mounted_directory_or_comparison_apis(self):
        ws = StorageWorkspace.__new__(StorageWorkspace)
        ws.request = AsyncMock(return_value={'entries': []})
        ws.pair = SimpleNamespace(active=False)
        await ws.read_directory('photos-5', '2026/2026-08', offset=150)
        self.assertEqual(ws.request.await_args.args, ('GET', '/api/photos/libraries/5/browse'))
        self.assertEqual(ws.request.await_args.kwargs['params']['offset'], 150)
        pane = BrowserPane.__new__(BrowserPane)
        pane.workspace, pane.volume_id, pane.view_mode = ws, 'photos-5', 'tree'
        self.assertIsNone(pane.scope())
        self.assertIsNone(pane.size_scope())
        pane.view_mode, pane.preview = 'preview', SimpleNamespace(volume_id='photos-5')
        self.assertIsNone(pane.scope())
