<template>
  <div ref="chartRef" :style="{ width, height }"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
  width: { type: String, default: '100%' },
  height: { type: String, default: '380px' },
  disableVisualMapRangeDrag: { type: Boolean, default: false }
})

const chartRef = ref(null)
let chartInstance = null

const disableVisualMapRangeDrag = () => {
  if (!props.disableVisualMapRangeDrag || !chartInstance) return

  // ECharts has no option to disable dragging the selected range as a whole.
  chartInstance.getZr().storage.getDisplayList().forEach(element => {
    if (element.type === 'polygon' && element.draggable && element.cursor === 'ns-resize') {
      element.draggable = false
    }
  })
}

const initChart = () => {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption(props.option, true)
  disableVisualMapRangeDrag()
}

const resizeChart = () => {
  chartInstance?.resize()
}

onMounted(async () => {
  await nextTick()
  initChart()
  window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
  chartInstance = null
})

watch(() => props.option, (newOpt) => {
  if (chartInstance) {
    chartInstance.setOption(newOpt, true)
    disableVisualMapRangeDrag()
  }
}, { deep: true })
</script>
