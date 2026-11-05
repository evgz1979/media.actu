export default {
  template: `
    <div class="pair-tree">
    <button v-if="root_file_count" class="pair-root-files" :aria-expanded="root_files_open" @click="$emit('toggle_files')">
      <i class="material-icons" aria-hidden="true">{{ root_files_open ? 'expand_more' : 'chevron_right' }}</i>
      Файлы в этой папке · различий: {{ root_file_count }}
    </button>
    <div class="pair-virtual" ref="viewport" @scroll="scrolled" @keydown="keyDown" @pointerdown="keyboardCursor=null" tabindex="0" :aria-label="side === 'left' ? 'Дерево основной папки' : 'Дерево копии'">
      <div v-if="!rows.length && !(root_file_count && !root_files_open)" class="pair-empty">{{ empty_text }}</div>
      <div v-else :style="{height: (rows.length * 28) + 'px', position:'relative'}" role="tree">
        <div v-for="(row, i) in visible" :key="row.path" role="treeitem" :aria-selected="selection === row.path"
          :aria-level="row.level + 1" :aria-expanded="row.kind === 'directory' ? !row.collapsed : undefined"
          :class="['pair-row', 'pair-' + row.status, {ghost: !row[side], selected: selection === row.path, alt: (start+i)%2}]"
          :style="{top: ((start+i)*28)+'px', paddingLeft: (5 + Math.min(row.level,14)*13)+'px'}"
          @click="pick(row)" @dblclick.prevent="$emit('open', {path:row.path,side})"
          tabindex="0"
          @keydown.enter.prevent="$emit('open', {path:row.path,side})" @keydown.space.prevent="$emit('select', {path:row.path,side})">
          <q-menu touch-position context-menu @before-show="$emit('menu_state', {open:true})" @hide="$emit('menu_state', {open:false})">
            <q-list dense>
              <q-item clickable v-close-popup :disable="!row[side]" @click.stop="$emit('context', {path:row.path,side,action:'finder'})">
                <q-item-section>Открыть в Finder</q-item-section>
              </q-item>
              <q-item clickable v-close-popup :disable="!row[side]" @click.stop="$emit('context', {path:row.path,side,action:'properties'})">
                <q-item-section>Свойства</q-item-section>
              </q-item>
              <q-item v-if="row.status === 'extra_copy' && side === 'right'" clickable v-close-popup @click.stop="$emit('context', {path:row.path,side,action:'decide'})">
                <q-item-section>Только в копии</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
          <button v-if="row.kind === 'directory'" class="pair-toggle" :aria-label="row.collapsed ? 'Раскрыть папку' : 'Свернуть папку'"
            @click.stop="$emit('toggle', {path:row.path,side})" @dblclick.stop><i class="material-icons" aria-hidden="true">{{ row.collapsed ? 'chevron_right' : 'expand_more' }}</i></button>
          <span v-else class="pair-toggle-spacer"></span>
          <i class="material-icons pair-file-icon" aria-hidden="true">{{ row.kind === 'directory' ? 'folder' : 'insert_drive_file' }}</i>
          <span class="pair-row-name">{{ row.name }}</span>
          <span v-if="row.attention_count" class="pair-attention" :aria-label="'Различий внутри: '+row.attention_count">{{ row.file_attention_count ? 'Файлы: '+row.file_attention_count : row.attention_count }}</span>
          <span v-if="row.decision && side === 'right'" class="pair-decision">{{ decisions[row.decision] }}</span>
          <span v-if="row[side]?.kind === 'directory' || row[side]?.size_text" class="pair-size">{{ row[side].kind === 'directory' ? (sizes[row[side].path] || '…') : row[side].size_text }}</span>
          <button v-if="row.status === 'extra_copy' && side === 'right'" class="pair-row-state pair-decide"
            @click.stop="$emit('context',{path:row.path,side,action:'decide'})">Только в копии</button>
          <span v-else class="pair-row-state">{{ status(row) }}</span>
        </div>
      </div>
    </div></div>`,
  props: {rows:Array, side:String, selected:String, empty_text:String, root_file_count:Number, root_files_open:Boolean, sizes:Object},
  emits: ['select','open','toggle','context','toggle_files','menu_state'],
  //: Создаёт локальное состояние видимой области, выбора и подписей решений.
  //: Серверные строки поступают через props; локальный курсор отвечает за клавиатуру.
  data() { return {top:0, height:400, observer:null, selection:this.selected, keyboardCursor:null, decisions:{keep:'Оставить',add_main:'В 00-main',move:'Перенос',remove:'Удаление'}}; },
  watch: {
    //: Сбрасывает клавиатурную позицию при замене списка строк.
    //: Новая выборка должна повторно найти текущий путь перед перемещением.
    rows() {this.keyboardCursor=null;},
    //: Принимает выбранный сервером путь и согласует локальное выделение.
    //: Сбрасывает курсор только при отсутствии фокуса внутри viewport.
    selected(value) {
      this.selection=value;
      if (!this.$refs.viewport?.contains(document.activeElement)) this.keyboardCursor=null;
    }},
  computed: {
    //: Вычисляет индекс первой отображаемой строки с запасом перед видимой областью.
    //: Высота строки 28 px, запас составляет восемь строк.
    start() { return Math.max(0, Math.floor(this.top/28)-8); },
    //: Выбирает небольшой срез строк вокруг текущей прокрутки.
    //: К высоте viewport добавляет 16 строк запаса для плавного перемещения.
    visible() { return this.rows.slice(this.start, this.start+Math.ceil(this.height/28)+16); },
  },
  //: Подписывает viewport на изменение размера и прокручивает длинный путь к концу.
  //: ResizeObserver поддерживает актуальную высоту среза без полной отрисовки списка.
  mounted() {
    this.observer=new ResizeObserver(() => {this.height=this.$refs.viewport.clientHeight;});
    this.observer.observe(this.$refs.viewport);
    this.$nextTick(() => {
      const path=this.$el.closest('.commander-pane')?.querySelector('.pane-path');
      if (path) path.scrollLeft=path.scrollWidth;
    });
  },
  //: Освобождает ResizeObserver при удалении компонента дерева.
  //: Не оставляет наблюдатель привязанным к удалённому DOM-элементу.
  beforeUnmount() { this.observer?.disconnect(); },
  methods: {
    //: Выбирает строку мышью и передаёт path/side серверному обработчику.
    //: Сбрасывает отдельный клавиатурный курсор, сохраняя локальное выделение.
    pick(row) {
      this.keyboardCursor=null;
      this.selection=row.path;
      this.$emit('select',{path:row.path,side:this.side});
    },
    //: Перемещает выделение стрелками вверх и вниз и удерживает строку в viewport.
    //: Игнорирует модификаторы, ввод текста, IME и открытые меню; отправляет keyboard=true.
    keyDown(event) {
      if (!['ArrowUp','ArrowDown'].includes(event.key) || event.ctrlKey || event.metaKey || event.altKey || event.shiftKey || event.isComposing) return;
      if (event.target.closest('input,textarea,select,[contenteditable="true"],[role="menu"],.q-menu')) return;
      if (!this.rows.length) return;
      event.preventDefault(); event.stopPropagation();
      const current=this.keyboardCursor ?? this.selection;
      const index=this.rows.findIndex(row=>row.path===current);
      const next=index<0 ? (event.key==='ArrowDown' ? 0 : this.rows.length-1) : Math.max(0,Math.min(this.rows.length-1,index+(event.key==='ArrowDown' ? 1 : -1)));
      if (index===next) return;
      const row=this.rows[next], viewport=this.$refs.viewport;
      this.keyboardCursor=this.selection=row.path;
      if (next*28<viewport.scrollTop) viewport.scrollTop=next*28;
      else if ((next+1)*28>viewport.scrollTop+viewport.clientHeight) viewport.scrollTop=(next+1)*28-viewport.clientHeight;
      viewport.focus({preventScroll:true});
      this.scrolled();
      this.$emit('select',{path:row.path,side:this.side,keyboard:true});
    },
    //: Обновляет локальное выделение по команде Python-обёртки.
    //: Путь должен соответствовать строке; функция сама не отправляет select.
    setSelection(path) {this.selection=path;},
    //: Возвращает список к верхней строке и согласует вторую сторону пары.
    //: Повторно вычисляет top через общий обработчик scrolled.
    resetScroll() { this.$refs.viewport.scrollTop=0; this.scrolled(); },
    //: Сохраняет положение viewport и синхронизирует вертикальную прокрутку пары.
    //: Обновляет соседний список только при расхождении более одного пикселя.
    scrolled() {
      this.top=this.$refs.viewport.scrollTop;
      const panes=this.$el.closest('.commander-trees')?.querySelectorAll('.pair-virtual') || [];
      for (const pane of panes) if (pane !== this.$refs.viewport && Math.abs(pane.scrollTop-this.top)>1) pane.scrollTop=this.top;
    },
    //: Выбирает пользовательскую подпись статуса строки для данной стороны пары.
    //: Отсутствующая сторона и непрочитанные элементы различаются явно.
    status(row) {
      if (!row[this.side]) {
        if (row.status === 'unverified') return 'Не проверено';
        return 'Отсутствует';
      }
      if (row.kind === 'directory' && row.status === 'both' && row.attention_count) return 'Есть различия';
      return {both:'Есть в обеих',missing_copy:'Нет в копии',extra_copy:'Только в копии',same:'Совпадает',same_size:'Имя и размер совпали',
        different:'Отличается',size_different:'Размер отличается',copy_incomplete:'Копия не завершена',conflict:'Разный тип',unverified:'Не проверено',skipped:'Не сравнивается'}[row.status] || '';
    },
  },
};
