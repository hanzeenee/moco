<template>
  <div ref="picker" class="language-picker" @keydown="handleKey">
    <button ref="trigger" class="language-trigger" type="button" :aria-label="$t('언어 선택')" aria-haspopup="menu" :aria-expanded="open" aria-controls="language-menu" @click="open = !open" @keydown.down.prevent="openMenu">
      <span>{{ language.locale === 'en' ? 'EN' : 'KR' }}</span><span class="mdi mdi-chevron-down" aria-hidden="true"></span>
    </button>
    <div v-if="open" id="language-menu" class="language-menu" role="menu" :aria-label="$t('언어 선택')">
      <span class="language-heading">Language</span>
      <button v-for="option in options" :key="option.value" type="button" role="menuitemradio" :aria-checked="language.locale === option.value" :lang="option.value" @click="choose(option.value)">
        <span class="language-code">{{ option.code }}</span><span>{{ option.label }}</span><span v-if="language.locale === option.value" class="mdi mdi-check" aria-hidden="true"></span>
      </button>
    </div>
  </div>
</template>
<script>
import { languageState, setLanguage } from '../i18n'
export default {
  name: 'LanguagePicker',
  setup() { return { language: languageState } },
  data() { return { open: false, options: [{ value: 'ko', code: 'KR', label: '한국어' }, { value: 'en', code: 'EN', label: 'English' }] } },
  mounted() { document.addEventListener('pointerdown', this.outside) },
  beforeUnmount() { document.removeEventListener('pointerdown', this.outside) },
  methods: {
    outside(event) { if (!this.$refs.picker.contains(event.target)) this.open = false },
    choose(value) { setLanguage(value); this.open = false; this.$refs.trigger.focus() },
    openMenu() { this.open = true; this.$nextTick(() => this.$refs.picker.querySelector('[role="menuitemradio"]')?.focus()) },
    handleKey(event) {
      if (event.key === 'Escape') { this.open = false; this.$refs.trigger.focus() }
      if (event.key === 'Tab') this.open = false
      if (!this.open || event.target === this.$refs.trigger) return
      const buttons = Array.from(this.$refs.picker.querySelectorAll('[role="menuitemradio"]'))
      const index = buttons.indexOf(document.activeElement)
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') { event.preventDefault(); buttons[(index + (event.key === 'ArrowDown' ? 1 : buttons.length - 1)) % buttons.length]?.focus() }
      if (event.key === 'Home' || event.key === 'End') { event.preventDefault(); buttons[event.key === 'Home' ? 0 : buttons.length - 1]?.focus() }
    },
  },
}
</script>
<style scoped>
.language-picker { position: relative; flex: 0 0 auto; z-index: 20; }
.language-trigger { display: flex; align-items: center; justify-content: center; gap: 7px; width: 76px; min-height: 34px; padding: 6px 11px; border: 1px solid #41444a; border-radius: 999px; background: #101113; color: #e9ecf0; font: inherit; font-size: 13px; cursor: pointer; }
.language-trigger .mdi { color: #9ba3af; font-size: 16px; }
.language-trigger:hover, .language-trigger[aria-expanded=true] { border-color: #9c862d; }
.language-menu { position: absolute; top: calc(100% + 12px); right: 0; width: 188px; box-sizing: border-box; padding: 8px; border: 1px solid #363a41; border-radius: 12px; background: #131416; box-shadow: 0 12px 35px #000b; color: #e6e9ee; }
.language-heading { display: block; padding: 7px 10px; color: #9099a7; font-size: 11px; }
.language-menu button { display: flex; align-items: center; gap: 10px; width: 100%; min-height: 42px; padding: 9px 10px; border: 0; border-radius: 7px; background: transparent; color: inherit; font: inherit; font-size: 13px; text-align: left; cursor: pointer; }
.language-menu button:hover { background: #242629; }
.language-menu button[aria-checked=true] { background: #28240e; color: #ffd000; }
.language-menu button>.mdi { margin-left: auto; }
.language-code { color: #939ca9; font-size: 11px; }
.language-trigger:focus-visible, .language-menu button:focus-visible { outline: 2px solid #ffd000; outline-offset: 3px; }
@media(max-width: 600px) { .language-trigger { width: 64px; min-height: 34px; padding: 6px 8px; gap: 4px; font-size: 12px; } }
@media(pointer: coarse) { .language-trigger { min-height: 44px; } .language-menu button { min-height: 44px; } }
</style>
