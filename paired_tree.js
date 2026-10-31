export default {
  template: `
    <div class="pair-tree">
    <button v-if="root_file_count" class="pair-root-files" :aria-expanded="root_files_open" @click="$emit('toggle_files')">
      <i class="material-icons" aria-hidden="true">{{ root_files_open ? 'expand_more' : 'chevron_right' }}</i>
      Файлы в этой папке · различий: {{ root_file_count }}
    </button>
    <div class="pair-virtual" ref="viewport" @scroll="scrolled" tabindex="0" :aria-label="side === 'left' ? 'Дерево основной папки' : 'Дерево копии'">
      <div v-if="!rows.length && !(root_file_count && !root_files_open)" class="pair-empty">{{ empty_text }}</div>
      <div v-else :style="{height: (rows.length * 28) + 'px', position:'relative'}" role="tree">
        <div v-for="(row, i) in visible" :key="row.path" role="treeitem" :aria-selected="selection === row.path"
          :aria-level="row.level + 1" :aria-expanded="row.kind === 'directory' ? !row.collapsed : undefined"
          :class="['pair-row', 'pair-' + row.status, {ghost: !row[side], selected: selection === row.path, alt: (start+i)%2}]"
          :style="{top: ((start+i)*28)+'px', paddingLeft: (5 + Math.min(row.level,14)*13)+'px'}"
          @click="$emit('select', {path:row.path,side})" @dblclick.prevent="$emit('open', {path:row.path,side})"
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
  data() { return {top:0, height:400, observer:null, selection:this.selected, decisions:{keep:'Оставить',add_main:'В 00-main',move:'Перенос',remove:'Удаление'}}; },
  watch: {selected(value) {this.selection=value;}},
  computed: {
    start() { return Math.max(0, Math.floor(this.top/28)-8); },
    visible() { return this.rows.slice(this.start, this.start+Math.ceil(this.height/28)+16); },
  },
  mounted() {
    this.observer=new ResizeObserver(() => {this.height=this.$refs.viewport.clientHeight;});
    this.observer.observe(this.$refs.viewport);
    this.$nextTick(() => {
      const path=this.$el.closest('.commander-pane')?.querySelector('.pane-path');
      if (path) path.scrollLeft=path.scrollWidth;
    });
  },
  beforeUnmount() { this.observer?.disconnect(); },
  methods: {
    setSelection(path) {this.selection=path;},
    resetScroll() { this.$refs.viewport.scrollTop=0; this.scrolled(); },
    scrolled() {
      this.top=this.$refs.viewport.scrollTop;
      const panes=this.$el.closest('.commander-trees')?.querySelectorAll('.pair-virtual') || [];
      for (const pane of panes) if (pane !== this.$refs.viewport && Math.abs(pane.scrollTop-this.top)>1) pane.scrollTop=this.top;
    },
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
