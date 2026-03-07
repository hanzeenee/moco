<template>
  <div class="page-area">
    <div class="page-title">강의 페이지</div>
  </div>
</template>

<script>
export default {
  name: 'LectureView'
}
</script>

<style scoped>
.page-area {
  background: #000000;
  min-height: calc(100vh - 56px);
  display: flex;
  justify-content: center;
  align-items: center;
}

.page-title {
  color: #ffffff;
  font-size: 40px;
  font-weight: bold;
}
</style>