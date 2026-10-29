<template>
  <header class="topbar">
    <button class="brand" type="button" aria-label="MOCONIX 홈" @click="goHome">
      <img class="brand-logo" src="@/assets/brand/moconix-wordmark.png" alt="MOCONIX" />
    </button>
    <a class="youtube-link" href="https://www.youtube.com/" target="_blank" rel="noopener noreferrer" aria-label="YouTube 새 탭으로 열기"><img class="youtube-logo" src="../assets/brand/youtube-wordmark.png" alt="YouTube" /></a>
  </header>
</template>

<script>
export default {
  name: 'TopBar',
  emits: ['go-home'],
  methods: {
    goHome() {
      this.$emit('go-home')
    }
  }
}
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  min-height: 88px;
  padding: 22px max(var(--page-gutter), calc((100% - var(--page-width)) / 2 + var(--page-gutter)));
  border-bottom: 1px solid #202328;
  background: #000;
  box-sizing: border-box;
}
.brand { position: relative; display: block; width: 184px; max-width: 100%; min-width: 0; flex: 0 1 184px; height: 38px; padding: 0; border: 0; background: transparent; cursor: pointer; overflow: hidden; }
/* Frame the supplied wordmark without changing its proportions. */
.brand-logo { position: absolute; top: 50%; left: -9%; display: block; width: 118%; max-width: none; height: auto; transform: translateY(-50%); }
.brand:focus-visible { outline: 2px solid #ffd000; outline-offset: 6px; border-radius: 3px; }
.youtube-link { position: relative; display: block; flex: 0 0 116px; width: 116px; height: 28px; overflow: hidden; border-radius: 3px; transition: opacity .16s; }
/* Crop only the supplied image margins; retain the logo proportions. */
.youtube-logo { position: absolute; width: 124.3%; max-width: none; height: auto; left: -11.5%; top: 50%; transform: translateY(-50%); }
.youtube-link:hover { opacity: .8; }
.youtube-link:focus-visible { outline: 2px solid #ffd000; outline-offset: 6px; }
@media (prefers-reduced-motion: reduce) { .youtube-link { transition: none; } }
@media (max-width: 600px) {
  .topbar { min-height: 72px; gap: 16px; padding-top: 18px; padding-bottom: 18px; }
  .brand { width: 156px; flex-basis: 156px; height: 32px; }
  .youtube-link { flex-basis: 96px; width: 96px; height: 24px; }
}
</style>
