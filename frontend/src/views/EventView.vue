<template>
  <div class="event-page">
    <div class="event-box left-box">
      이벤트1
    </div>

    <div class="event-box right-box">
      이벤트2
    </div>
  </div>
</template>

<script>
export default {
  name: 'EventView'
}
</script>

<style scoped>
.event-page {
  background: #000000;
  min-height: calc(100vh - 56px);
  display: flex;
}

.event-box {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #ffffff;
  font-size: 36px;
  font-weight: bold;
}

.left-box {
  border-right: 1px solid #333333;
}

.right-box {
  border-left: 1px solid #111111;
}
</style>