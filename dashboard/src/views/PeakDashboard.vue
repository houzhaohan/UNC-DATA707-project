<template>
  <div>
    <div class="section-header">
      <div>
        <h2>⏰ Peak vs Off-Peak Analysis</h2>
        <p>Comparison of Peak vs. Non-Peak Operating Periods · 24-Hour Traffic Distribution</p>
      </div>
      <el-tag type="warning" effect="plain">2026 Dataset</el-tag>
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
      <!-- Grouped Bar Chart: Peak vs Off-Peak -->
      <el-col :xs="24" :lg="14">
        <div class="card">
          <div class="card-title">Peak vs Off-Peak Comparison</div>
          <BaseChart :option="groupedBarOption" />
        </div>
      </el-col>

      <!-- Period Detail Bar -->
      <el-col :xs="24" :lg="10">
        <div class="card">
          <div class="card-title">Detailed Period Breakdown</div>
          <BaseChart :option="periodDetailOption" />
        </div>
      </el-col>
    </el-row>

    <!-- Line Chart: Hourly Records & Trips -->
    <el-row :gutter="20">
      <el-col :xs="24">
        <div class="card">
          <div class="card-title">24-Hour Traffic Pattern (Records & Trips)</div>
          <BaseChart :option="hourlyLineOption" height="380px" />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- Heatmap: Hourly pattern -->
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div class="card-title">Hourly Records Heatmap</div>
          <BaseChart :option="hourlyHeatmapOption" height="340px" disable-visual-map-range-drag />
        </div>
      </el-col>

      <!-- Route Peak Comparison -->
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div class="card-title">Route Records: Peak vs Off-Peak</div>
          <BaseChart :option="routePeakGroupedOption" height="340px" />
        </div>
      </el-col>
    </el-row>

    <!-- Calendar-style hourly ridgeline -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="14">
        <div class="card">
          <div class="card-title">Hourly Avg Dwell & Headway</div>
          <BaseChart :option="dwellHeadwayOption" height="320px" />
        </div>
      </el-col>
      <!-- Summary table -->
      <el-col :xs="24" :lg="10">
        <div class="card">
          <div class="card-title">Period Summary</div>
          <el-table :data="periodSummary" stripe size="small" height="320" style="width: 100%">
            <el-table-column prop="period_detail" label="Period" min-width="120">
              <template #default="{ row }">
                <el-tag :type="periodTagType(row.period_detail)" size="small">{{ row.period_detail }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Records" min-width="95">
              <template #default="{ row }">{{ formatNum(row.total_records) }}</template>
            </el-table-column>
            <el-table-column label="Trips" min-width="85">
              <template #default="{ row }">{{ formatNum(row.total_trips) }}</template>
            </el-table-column>
            <el-table-column label="Dwell(s)" min-width="80">
              <template #default="{ row }">{{ row.avg_dwell_time_seconds?.toFixed(1) }}</template>
            </el-table-column>
            <el-table-column label="Headway(s)" min-width="90">
              <template #default="{ row }">{{ row.avg_headway_seconds?.toFixed(0) }}</template>
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

const peakData = ref([])
const periodData = ref([])
const hourlyData = ref([])
const routePeakData = ref([])

onMounted(async () => {
  const [p, pd, h, rp] = await Promise.all([
    fetch('/data/peak_comparison.json').then(r => r.json()),
    fetch('/data/period_detail.json').then(r => r.json()),
    fetch('/data/hourly.json').then(r => r.json()),
    fetch('/data/route_peak.json').then(r => r.json())
  ])
  peakData.value = p
  periodData.value = pd
  hourlyData.value = h
  routePeakData.value = rp
})

const formatNum = n => Number(n).toLocaleString()

const periodTagType = name => {
  if (name === 'Morning Peak' || name === 'Evening Peak') return 'danger'
  if (name === 'Off-Peak') return 'info'
  return 'success'
}

const kpis = computed(() => {
  const peak = peakData.value.find(p => p.period_type === 'Peak') || {}
  const off = peakData.value.find(p => p.period_type === 'Off-Peak') || {}
  const ratio = off.total_records ? (peak.total_records / off.total_records) : 0
  return [
    { value: formatNum(peak.total_records || 0), label: 'Peak Records' },
    { value: formatNum(off.total_records || 0), label: 'Off-Peak Records' },
    { value: ratio.toFixed(2), label: 'Peak/Off-Peak Ratio' },
    { value: peak.avg_headway_seconds?.toFixed(0) + 's' || '-', label: 'Peak Headway' }
  ]
})

const periodSummary = computed(() => periodData.value)

// Grouped Bar: Peak vs Off-Peak multiple metrics
const groupedBarOption = computed(() => {
  const p = peakData.value
  if (!p.length) return {}

  const labels = ['Records', 'Trips', 'Avg Dwell (s)', 'Avg Headway (s)']
  const peakRow = p.find(x => x.period_type === 'Peak')
  const offRow = p.find(x => x.period_type === 'Off-Peak')

  const peakVals = [
    peakRow.total_records,
    peakRow.total_trips,
    Math.round(peakRow.avg_dwell_time_seconds * 10) / 10,
    Math.round(peakRow.avg_headway_seconds)
  ]
  const offVals = [
    offRow.total_records,
    offRow.total_trips,
    Math.round(offRow.avg_dwell_time_seconds * 10) / 10,
    Math.round(offRow.avg_headway_seconds)
  ]

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#0f172a' }
    },
    legend: {
      data: ['Peak', 'Off-Peak'],
      top: 0,
      textStyle: { color: '#64748b' }
    },
    grid: { left: 80, right: 40, top: 50, bottom: 50 },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { color: '#64748b', fontSize: 12 }
    },
    yAxis: {
      type: 'log',
      name: 'Log Scale',
      nameTextStyle: { color: '#64748b' },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#64748b', formatter: v => v >= 1000 ? (v / 1000).toFixed(0) + 'K' : v }
    },
    series: [
      {
        name: 'Peak',
        type: 'bar',
        emphasis: { itemStyle: { shadowBlur: 18, shadowColor: 'rgba(0,0,0,0.28)', shadowOffsetY: 3 } },
        data: peakVals,
        barGap: '10%',
        barWidth: '35%',
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#ef4444' },
            { offset: 1, color: '#fca5a5' }
          ])
        }
      },
      {
        name: 'Off-Peak',
        type: 'bar',
        emphasis: { itemStyle: { shadowBlur: 18, shadowColor: 'rgba(0,0,0,0.28)', shadowOffsetY: 3 } },
        data: offVals,
        barWidth: '35%',
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#10b981' },
            { offset: 1, color: '#6ee7b7' }
          ])
        }
      }
    ]
  }
})

// Period detail pie-like bar
const periodDetailOption = computed(() => {
  const palette = { 'Morning Peak': '#f59e0b', 'Evening Peak': '#ef4444', 'Off-Peak': '#10b981' }
  const order = ['Morning Peak', 'Off-Peak', 'Evening Peak']
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 40, top: 40, bottom: 30 },
    xAxis: { type: 'value', axisLabel: { color: '#64748b', formatter: v => (v / 1000000).toFixed(1) + 'M' }, splitLine: { lineStyle: { color: '#f1f5f9' } } },
    yAxis: { type: 'category', data: order, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#475569' } },
    series: [{
      type: 'bar',
      emphasis: { itemStyle: { shadowBlur: 18, shadowColor: 'rgba(0,0,0,0.28)', shadowOffsetY: 3 } },
      data: order.map(p => {
        const row = periodData.value.find(x => x.period_detail === p) || { total_records: 0 }
        return {
          value: row.total_records,
          name: p,
          itemStyle: {
            borderRadius: [0, 6, 6, 0],
            color: palette[p]
          }
        }
      }),
      barWidth: '50%',
      label: {
        show: true,
        position: 'right',
        formatter: p => (p.value / 1000000).toFixed(2) + 'M',
        color: '#475569',
        fontSize: 11,
        fontWeight: 600
      }
    }]
  }
})

// Hourly line chart
const hourlyLineOption = computed(() => {
  const data = hourlyData.value
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#0f172a' }
    },
    legend: {
      data: ['Records', 'Trips'],
      top: 0,
      textStyle: { color: '#64748b' }
    },
    grid: { left: 70, right: 60, top: 50, bottom: 50 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.hour + ':00'),
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { color: '#64748b', fontSize: 11, interval: 1 }
    },
    yAxis: [
      {
        type: 'value',
        name: 'Records',
        nameTextStyle: { color: '#64748b' },
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f1f5f9' } },
        axisLabel: { color: '#64748b', formatter: v => (v / 1000).toFixed(0) + 'K' }
      },
      {
        type: 'value',
        name: 'Trips',
        nameTextStyle: { color: '#64748b' },
        axisLine: { show: false },
        splitLine: { show: false },
        axisLabel: { color: '#64748b', formatter: v => (v / 1000).toFixed(0) + 'K' }
      }
    ],
    series: [
      {
        name: 'Records',
        type: 'line',
        data: data.map(d => d.total_records),
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 3, color: '#0ea5e9' },
        itemStyle: { color: '#0ea5e9' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(14, 165, 233, 0.35)' },
            { offset: 1, color: 'rgba(14, 165, 233, 0.02)' }
          ])
        },
        markArea: {
          silent: true,
          itemStyle: { opacity: 0.12 },
          data: [
            [{ xAxis: '7:00', itemStyle: { color: '#f59e0b' } }, { xAxis: '9:00' }],
            [{ xAxis: '16:00', itemStyle: { color: '#ef4444' } }, { xAxis: '18:00' }]
          ]
        }
      },
      {
        name: 'Trips',
        type: 'line',
        yAxisIndex: 1,
        data: data.map(d => d.total_trips),
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2.5, color: '#10b981', type: 'dashed' },
        itemStyle: { color: '#10b981' }
      }
    ]
  }
})

// Heatmap: hourly pattern (single-row heatmap for calendar-style look)
const hourlyHeatmapOption = computed(() => {
  const data = hourlyData.value
  const maxRec = Math.max(1, ...data.map(d => d.total_records))
  const maxDwell = Math.max(...data.map(d => d.avg_dwell_time_seconds))

  return {
    tooltip: {
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#0f172a' },
      formatter: p => {
        const row = data[p.data[0]]
        return `<b>${row.hour}:00 - ${row.hour}:59</b><br/>Records: ${formatNum(row.total_records)}<br/>Trips: ${formatNum(row.total_trips)}`
      }
    },
    grid: { left: 20, right: 100, top: 40, bottom: 52 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.hour),
      splitArea: { show: true },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#64748b', fontSize: 10, formatter: '{value}:00' }
    },
    yAxis: {
      type: 'category',
      data: ['Hour'],
      splitArea: { show: true },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { show: false }
    },
    visualMap: {
      min: 0,
      max: maxRec,
      calculable: true,
      indicatorSize: 0,
      orient: 'vertical',
      right: 12,
      top: 'center',
      itemWidth: 12,
      itemHeight: 150,
      textStyle: { color: '#64748b' },
      inRange: {
        color: ['#ecfdf5', '#a7f3d0', '#34d399', '#059669', '#047857']
      }
    },
    series: [
      {
        type: 'heatmap',
        name: 'Records',
        data: data.map((d, i) => [i, 0, d.total_records]),
        label: { show: true, color: '#0f172a', fontSize: 9, formatter: p => data[p.data[0]].hour },
        itemStyle: { borderColor: '#fff', borderWidth: 3, borderRadius: 4 }
      }
    ]
  }
})

// Route peak grouped bar
const routePeakGroupedOption = computed(() => {
  const data = routePeakData.value
  const routes = [...new Set(data.map(d => d.route_id))]
  const peakVals = routes.map(r => {
    const row = data.find(d => d.route_id === r && d.period_type === 'Peak')
    return row ? row.total_records : 0
  })
  const offVals = routes.map(r => {
    const row = data.find(d => d.route_id === r && d.period_type === 'Off-Peak')
    return row ? row.total_records : 0
  })

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#0f172a' }
    },
    legend: { data: ['Peak', 'Off-Peak'], top: 0, textStyle: { color: '#64748b' } },
    grid: { left: 60, right: 30, top: 50, bottom: 40 },
    xAxis: {
      type: 'category',
      data: routes,
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { color: '#64748b' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#64748b', formatter: v => (v / 1000000).toFixed(1) + 'M' },
      splitLine: { lineStyle: { color: '#f1f5f9' } }
    },
    series: [
      {
        name: 'Peak',
        type: 'bar',
        emphasis: { itemStyle: { shadowBlur: 18, shadowColor: 'rgba(0,0,0,0.28)', shadowOffsetY: 3 } },
        stack: 'total',
        data: peakVals,
        itemStyle: { color: '#ef4444', borderRadius: [0, 0, 0, 0] }
      },
      {
        name: 'Off-Peak',
        type: 'bar',
        emphasis: { itemStyle: { shadowBlur: 18, shadowColor: 'rgba(0,0,0,0.28)', shadowOffsetY: 3 } },
        stack: 'total',
        data: offVals,
        itemStyle: { color: '#10b981', borderRadius: [4, 4, 0, 0] }
      }
    ]
  }
})

// Dwell & Headway dual-axis line
const dwellHeadwayOption = computed(() => {
  const data = hourlyData.value
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' }, backgroundColor: 'rgba(255,255,255,0.95)', borderColor: '#e2e8f0', textStyle: { color: '#0f172a' } },
    legend: { data: ['Avg Dwell Time (s)', 'Avg Headway (s)'], top: 0, textStyle: { color: '#64748b' } },
    grid: { left: 60, right: 70, top: 50, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.hour + 'h'),
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { color: '#64748b', fontSize: 11, interval: 1 }
    },
    yAxis: [
      { type: 'value', name: 'Dwell (s)', nameTextStyle: { color: '#64748b' }, axisLabel: { color: '#64748b' }, splitLine: { lineStyle: { color: '#f1f5f9' } } },
      { type: 'value', name: 'Headway (s)', nameTextStyle: { color: '#64748b' }, axisLabel: { color: '#64748b' }, splitLine: { show: false } }
    ],
    series: [
      {
        name: 'Avg Dwell Time (s)',
        type: 'line',
        smooth: true,
        data: data.map(d => d.avg_dwell_time_seconds),
        symbolSize: 4,
        lineStyle: { width: 2.5, color: '#8b5cf6' },
        itemStyle: { color: '#8b5cf6' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
            { offset: 1, color: 'rgba(139, 92, 246, 0.02)' }
          ])
        }
      },
      {
        name: 'Avg Headway (s)',
        type: 'line',
        yAxisIndex: 1,
        smooth: true,
        data: data.map(d => d.avg_headway_seconds),
        symbolSize: 4,
        lineStyle: { width: 2.5, color: '#f59e0b' },
        itemStyle: { color: '#f59e0b' }
      }
    ]
  }
})
</script>

<style scoped>
.kpi-row {
  margin-bottom: 20px;
}
</style>
