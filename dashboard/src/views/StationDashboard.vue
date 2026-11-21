<template>
  <div>
    <div class="section-header">
      <div>
        <h2>🚉 Station Efficiency Analysis</h2>
        <p>2026 MBTA Station Operating Efficiency · 125+ Stations</p>
      </div>
      <el-tag type="success" effect="plain">2026 Dataset</el-tag>
    </div>

    <!-- KPI Cards -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :xs="12" :sm="6" v-for="kpi in kpis" :key="kpi.label">
        <div class="kpi-card">
          <div class="kpi-value">{{ kpi.value }}</div>
          <div class="kpi-label">{{ kpi.label }}</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- Scatter Plot: Records vs Dwell Time -->
      <el-col :xs="24" :lg="14">
        <div class="card">
          <div class="card-title">Records vs Avg Dwell Time (Outliers Filtered)</div>
          <BaseChart :option="scatterOption" />
        </div>
      </el-col>

      <!-- Box Plot: Dwell Time Distribution -->
      <el-col :xs="24" :lg="10">
        <div class="card">
          <div class="card-title">Dwell Time Distribution (Box Plot)</div>
          <BaseChart :option="boxOption" />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- Heatmap: Top 20 Stations by Records -->
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div class="card-title">Top Stations Records Heatmap</div>
          <BaseChart :option="heatmapOption" height="340px" disable-visual-map-range-drag />
        </div>
      </el-col>

      <!-- Bar: Top Dwell Time -->
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div class="card-title">Top 10 Stations by Avg Dwell Time</div>
          <BaseChart :option="topDwellOption" height="340px" />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- Bar: Top Record Stations -->
      <el-col :xs="24" :lg="14">
        <div class="card">
          <div class="card-title">Top 10 Stations by Record Count</div>
          <BaseChart :option="topRecordsOption" height="320px" />
        </div>
      </el-col>

      <!-- Station detail table -->
      <el-col :xs="24" :lg="10">
        <div class="card">
          <div class="card-title">Station Detail (Top 15)</div>
          <el-table :data="topStations" stripe size="small" height="320" style="width: 100%">
            <el-table-column prop="station_name" label="Station" min-width="150" />
            <el-table-column label="Records" min-width="105">
              <template #default="{ row }">{{ formatNum(row.total_records) }}</template>
            </el-table-column>
            <el-table-column label="Routes" min-width="75" prop="route_count" />
            <el-table-column label="Dwell(s)" min-width="85">
              <template #default="{ row }">{{ row.avg_dwell_time_seconds?.toFixed(0) }}</template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import BaseChart from '../components/BaseChart.vue'

const stationsData = ref([])
const dwellTopData = ref([])
const recordsTopData = ref([])

onMounted(async () => {
  const [s, d, r] = await Promise.all([
    fetch('/data/stations.json').then(r => r.json()),
    fetch('/data/stations_dwell_top.json').then(r => r.json()),
    fetch('/data/stations_records_top.json').then(r => r.json())
  ])
  stationsData.value = s
  dwellTopData.value = d
  recordsTopData.value = r
})

const formatNum = n => Number(n).toLocaleString()

const kpis = computed(() => {
  const d = stationsData.value
  if (!d.length) return []
  const totalRecords = d.reduce((a, r) => a + r.total_records, 0)
  const avgDwell = d.reduce((a, r) => a + (r.avg_dwell_time_seconds || 0), 0) / d.length
  const highDwell = d.filter(r => r.avg_dwell_time_seconds > 100).length
  return [
    { value: d.length, label: 'Stations Analyzed' },
    { value: formatNum(totalRecords), label: 'Total Records' },
    { value: avgDwell.toFixed(0) + 's', label: 'Mean Dwell Time' },
    { value: highDwell, label: 'High-Dwell Stations' }
  ]
})

const topStations = computed(() =>
  [...stationsData.value].sort((a, b) => b.total_records - a.total_records).slice(0, 15)
)

// Filter outliers for scatter (dwell < 200s keeps normal stations visible)
const filteredForScatter = computed(() =>
  stationsData.value.filter(s => s.avg_dwell_time_seconds < 200)
)

// Scatter Plot
const scatterOption = computed(() => ({
  tooltip: {
    backgroundColor: 'rgba(255,255,255,0.95)',
    borderColor: '#e2e8f0',
    textStyle: { color: '#0f172a' },
    formatter: p => `<b>${p.data[2]}</b><br/>Records: ${Number(p.data[0]).toLocaleString()}<br/>Dwell: ${p.data[1].toFixed(1)}s`
  },
  grid: { left: 70, right: 30, top: 30, bottom: 50 },
  xAxis: {
    type: 'log',
    name: 'Total Records (log scale)',
    nameTextStyle: { color: '#64748b' },
    axisLine: { lineStyle: { color: '#cbd5e1' } },
    splitLine: { lineStyle: { color: '#f1f5f9' } },
    axisLabel: { color: '#64748b' }
  },
  yAxis: {
    type: 'value',
    name: 'Avg Dwell Time (s)',
    nameTextStyle: { color: '#64748b' },
    axisLine: { lineStyle: { color: '#cbd5e1' } },
    splitLine: { lineStyle: { color: '#f1f5f9' } },
    axisLabel: { color: '#64748b' }
  },
  series: [{
    type: 'scatter',
    data: filteredForScatter.value.map(s => [s.total_records, s.avg_dwell_time_seconds, s.station_name]),
    symbolSize: d => Math.max(6, Math.sqrt(d[0]) / 30),
    itemStyle: {
      color: new echarts.graphic.RadialGradient(0.5, 0.5, 0.5, [
        { offset: 0, color: 'rgba(14, 165, 233, 0.9)' },
        { offset: 1, color: 'rgba(14, 165, 233, 0.4)' }
      ]),
      shadowBlur: 8,
      shadowColor: 'rgba(14, 165, 233, 0.3)'
    },
    emphasis: {
      itemStyle: { shadowBlur: 20, borderColor: '#0ea5e9', borderWidth: 2 },
      label: { show: true, formatter: p => p.data[2], fontSize: 12, color: '#0f172a' }
    }
  }]
}))

// Box Plot for dwell time
const boxOption = computed(() => {
  // Filter normal dwell times (< 500s) for a meaningful box plot
  const dwells = stationsData.value
    .map(s => s.avg_dwell_time_seconds)
    .filter(v => v != null && v < 500)
    .sort((a, b) => a - b)

  const q = (arr, p) => arr[Math.floor(p * arr.length)]
  const min = dwells[0]
  const max = dwells[dwells.length - 1]
  const q1 = q(dwells, 0.25)
  const median = q(dwells, 0.5)
  const q3 = q(dwells, 0.75)

  return {
    tooltip: {
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#0f172a' },
      formatter: () => `Min: ${min.toFixed(0)}s<br/>Q1: ${q1.toFixed(0)}s<br/>Median: ${median.toFixed(0)}s<br/>Q3: ${q3.toFixed(0)}s<br/>Max: ${max.toFixed(0)}s`
    },
    grid: { left: 60, right: 30, top: 20, bottom: 50 },
    xAxis: {
      type: 'category',
      data: ['Dwell Time (s)'],
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { color: '#64748b' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#64748b', formatter: '{value}s' }
    },
    series: [{
      type: 'boxplot',
      data: [[min, q1, median, q3, max]],
      itemStyle: {
        color: 'rgba(16, 185, 129, 0.5)',
        borderColor: '#10b981',
        borderWidth: 1,
        borderRadius: 6
      }
    }, {
      type: 'scatter',
      symbol: 'circle',
      symbolSize: 6,
      data: dwells.map(d => ['Dwell Time (s)', d]),
      itemStyle: { color: 'rgba(14, 165, 233, 0.4)' },
      jitter: 0.28
    }].map((s, i) => i === 0 ? s : { ...s, xAxisIndex: 0, yAxisIndex: 0 })
  }
})

// Heatmap: stations records
const heatmapOption = computed(() => {
  const top = [...stationsData.value].sort((a, b) => b.total_records - a.total_records).slice(0, 20)
  const names = top.map(s => s.station_name)
  const colors = ['route_count', 'platform_count', 'total_records']

  const maxRecords = Math.max(1, ...top.map(s => s.total_records / 1000))

  return {
    tooltip: {
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#0f172a' },
      formatter: p => {
        const [metricIndex, stationIndex, value] = p.value
        const metric = ['Routes', 'Platforms', 'Records (K)'][metricIndex]
        return `<b>${top[stationIndex].station_name}</b><br/>${metric}: ${metricIndex === 2 ? value.toFixed(1) : value}`
      }
    },
    grid: { left: 140, right: 110, top: 10, bottom: 40 },
    xAxis: {
      type: 'category',
      data: ['Routes', 'Platforms', 'Records (K)'],
      splitArea: { show: true },
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { color: '#64748b', fontSize: 11 }
    },
    yAxis: {
      type: 'category',
      data: names,
      splitArea: { show: true },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#334155', fontSize: 11 }
    },
    visualMap: {
      min: 0,
      max: maxRecords,
      calculable: true,
      indicatorSize: 0,
      orient: 'vertical',
      right: 15,
      top: 'center',
      itemWidth: 12,
      itemHeight: 150,
      textStyle: { color: '#64748b' },
      inRange: { color: ['#e0f2fe', '#7dd3fc', '#0ea5e9', '#0369a1'] }
    },
    series: [{
      type: 'heatmap',
      data: top.flatMap((s, i) => [
        [0, i, s.route_count],
        [1, i, s.platform_count],
        [2, i, s.total_records / 1000]
      ]),
      label: {
        show: true,
        formatter: p => {
          const value = p.value?.[2]
          return Number.isFinite(value) ? value.toFixed(p.value[0] === 2 ? 1 : 0) : ''
        },
        color: '#0f172a',
        fontSize: 10
      },
      itemStyle: { borderColor: '#fff', borderWidth: 2 }
    }]
  }
})

// Top dwell bar
const topDwellOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 140, right: 40, top: 20, bottom: 30 },
  xAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#f1f5f9' } },
    axisLabel: { color: '#64748b', formatter: '{value}s' }
  },
  yAxis: {
    type: 'category',
    data: [...dwellTopData.value].reverse().map(s => s.station_name),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#475569' }
  },
  series: [{
    type: 'bar',
    emphasis: { itemStyle: { shadowBlur: 18, shadowColor: 'rgba(0,0,0,0.28)', shadowOffsetY: 3 } },
    data: [...dwellTopData.value].reverse().map((s, i) => ({
      value: s.avg_dwell_time_seconds,
      itemStyle: {
        borderRadius: [0, 6, 6, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#ef4444' },
          { offset: 1, color: '#f87171' }
        ])
      }
    })),
    barWidth: '45%',
    label: {
      show: true,
      position: 'right',
      formatter: p => {
        const v = p.value
        return v > 60 ? (v / 60).toFixed(1) + ' min' : v.toFixed(0) + ' s'
      },
      color: '#475569',
      fontSize: 11,
      fontWeight: 600
    }
  }]
}))

// Top records bar
const topRecordsOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 140, right: 40, top: 20, bottom: 30 },
  xAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#f1f5f9' } },
    axisLabel: { color: '#64748b', formatter: v => (v / 1000).toFixed(0) + 'K' }
  },
  yAxis: {
    type: 'category',
    data: [...recordsTopData.value].reverse().map(s => s.station_name),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#475569' }
  },
  series: [{
    type: 'bar',
    emphasis: { itemStyle: { shadowBlur: 18, shadowColor: 'rgba(0,0,0,0.28)', shadowOffsetY: 3 } },
    data: [...recordsTopData.value].reverse().map(s => ({
      value: s.total_records,
      itemStyle: {
        borderRadius: [0, 6, 6, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#0ea5e9' },
          { offset: 1, color: '#38bdf8' }
        ])
      }
    })),
    barWidth: '50%',
    label: {
      show: true,
      position: 'right',
      formatter: p => Number(p.value).toLocaleString(),
      color: '#475569',
      fontSize: 11,
      fontWeight: 600
    }
  }]
}))
</script>

<style scoped>
.kpi-row {
  margin-bottom: 20px;
}
</style>
