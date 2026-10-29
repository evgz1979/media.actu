export default {
  template: `
    <div class="pair-virtual" ref="viewport" @scroll="scrolled" tabindex="0" :aria-label="side === 'left' ? 'Дерево основной папки' : 'Дерево копии'">
      <div v-if="!rows.length" class="pair-empty">{{ empty_text }}</div>
      <div v-else :style="{height: (rows.length * 28) + 'px', position:'relative'}" role="tree">
        <div v-for="(row, i) in visible" :key="row.path" role="treeitem" :aria-selected="selection === row.path"
          :aria-level="row.level + 1" :aria-expanded="row.kind === 'directory' ? !row.collapsed : undefined"
          :class="['pair-row', 'pair-' + row.status, {ghost: !row[side], selected: selection === row.path, alt: (start+i)%2}]"
          :style="{top: ((start+i)*28)+'px', paddingLeft: (5 + Math.min(row.level,14)*13)+'px'}"
          @click="$emit('select', {path:row.path,side})" @dblclick.prevent="$emit('open', {path:row.path,side})"
          @contextmenu.prevent="$emit('context', {path:row.path,side})" tabindex="0"
          @keydown.enter.prevent="$emit('open', {path:row.path,side})" @keydown.space.prevent="$emit('select', {path:row.path,side})">
          <button v-if="row.kind === 'directory'" class="pair-toggle" :aria-label="row.collapsed ? 'Раскрыть папку' : 'Свернуть папку'"
            @click.stop="$emit('toggle', {path:row.path,side})" @dblclick.stop><i class="material-icons" aria-hidden="true">{{ row.collapsed ? 'chevron_right' : 'expand_more' }}</i></button>
          <span v-else class="pair-toggle-spacer"></span>
          <i class="material-icons pair-file-icon" aria-hidden="true">{{ row.kind === 'directory' ? 'folder' : 'insert_drive_file' }}</i>
          <span class="pair-row-name">{{ row.name }}</span>
          <span v-if="row.attention_count" class="pair-attention" :aria-label="'Ниже требуют внимания: '+row.attention_count">{{ row.attention_count }}</span>
          <span v-if="row.decision && side === 'right'" class="pair-decision">{{ decisions[row.decision] }}</span>
          <span v-if="row[side]?.size_text" class="pair-size">{{ row[side].size_text }}</span>
          <button v-if="row.status === 'extra_copy' && side === 'right'" class="pair-row-state pair-decide"
            @click.stop="$emit('context',{path:row.path,side})">Только в копии</button>
          <span v-else class="pair-row-state">{{ status(row) }}</span>
        </div>
      </div>
    </div>`,
  props: {rows:Array, side:String, selected:String, empty_text:String},
  emits: ['select','open','toggle','context'],
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
        return this.side === 'left' ? 'Нет в 00-main' : 'Нет в копии';
      }
      return {both:'Есть в обоих',missing_copy:'Нет в копии',extra_copy:'Только в копии',same:'Совпадает',
        different:'Отличается',conflict:'Разный тип',unverified:'Не проверено',skipped:'Не сравнивается'}[row.status] || '';
    },
  },
};
