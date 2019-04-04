<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
body {
  background: #272727;
}
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #959595;
}
.c3-axis text{
  fill: #959595;
}
.c3-axis line{
  stroke: #959595;
}
.c3-axis path{
  stroke: #959595;
}
.c3-legend-item text{
  fill: #959595;
}
.c3-ygrid-line line {
  stroke: #93a1a1;
  fill: none;
  stroke-dasharray: 4 4;
}
.c3-xgrid-line line {
  stroke: #cb4b16;
}

</style>
