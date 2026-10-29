<template>
  <header class="topbar">
    <button class="brand" type="button" aria-label="MOCONIX 홈" @click="goHome">
      <img class="brand-logo" src="@/assets/brand/moconix-wordmark.png" alt="MOCONIX" />
    </button>
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
  min-height: 88px;
  padding: 22px max(var(--page-gutter), calc((100% - var(--page-width)) / 2 + var(--page-gutter)));
  border-bottom: 1px solid #202328;
  background: #000;
  box-sizing: border-box;
}
.brand { position: relative; display: block; width: 184px; max-width: 100%; height: 38px; padding: 0; border: 0; background: transparent; cursor: pointer; overflow: hidden; }
/* Frame the supplied wordmark without changing its proportions. */
.brand-logo { position: absolute; top: 50%; left: -9%; display: block; width: 118%; max-width: none; height: auto; transform: translateY(-50%); }
.brand:focus-visible { outline: 2px solid #ffd000; outline-offset: 6px; border-radius: 3px; }
@media (max-width: 600px) {
  .topbar { min-height: 72px; padding-top: 18px; padding-bottom: 18px; }
  .brand { width: 156px; height: 32px; }
}
</style>
