<template>
  <div>
    <div class="section-header">
      <div>
        <h2>🛣️ Route Performance Analysis</h2>
        <p>2026 MBTA Line Operating Performance Overview · 5 Main Lines</p>
      </div>
      <el-tag type="info" effect="plain">2026 Dataset</el-tag>
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
      <!-- Interactive Bar Chart -->
      <el-col :xs="24" :lg="14">
        <div class="card">
          <div class="card-title">Records by Route</div>
          <BaseChart :option="barOption" />
        </div>
      </el-col>

      <!-- Treemap -->
      <el-col :xs="24" :lg="10">
        <div class="card">
          <div class="card-title">Route Record Share</div>
          <BaseChart :option="treemapOption" />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- Radar Chart -->
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div class="card-title">Multi-Dimensional Comparison</div>
          <BaseChart :option="radarOption" />
        </div>
      </el-col>

      <!-- Route Detail Table -->
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div class="card-title">Route Metrics Detail</div>
          <el-table :data="routesData" stripe size="small" height="380" style="width: 100%">
            <el-table-column prop="route_name" label="Route" min-width="150" />
            <el-table-column label="Records" min-width="120">
              <template #default="{ row }">{{ formatNum(row.total_records) }}</template>
            </el-table-column>
            <el-table-column label="Trips" min-width="100">
              <template #default="{ row }">{{ formatNum(row.total_trips) }}</template>
            </el-table-column>
            <el-table-column label="Stops" min-width="80" prop="total_stops" />
            <el-table-column label="Travel(s)" min-width="95">
              <template #default="{ row }">{{ row.avg_travel_time_seconds?.toFixed(1) }}</template>
            </el-table-column>
            <el-table-column label="Dwell(s)" min-width="85">
              <template #default="{ row }">{{ row.avg_dwell_time_seconds?.toFixed(1) }}</template>
            </el-table-column>
            <el-table-column label="Headway(s)" min-width="105">
              <template #default="{ row }">{{ row.avg_headway_trunk_seconds?.toFixed(0) || '-' }}</template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- Dwell Time comparison -->
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div class="card-title">Average Dwell Time per Route</div>
          <BaseChart :option="dwellOption" height="320px" />
        </div>
      </el-col>
      <!-- Headway comparison -->
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div class="card-title">Average Headway per Route</div>
          <BaseChart :option="headwayOption" height="320px" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import BaseChart from '../components/BaseChart.vue'

const routesData = ref([])

onMounted(async () => {
  const res = await fetch('/data/routes.json')
  routesData.value = await res.json()
})

const formatNum = n => Number(n).toLocaleString()

const kpis = computed(() => {
  const d = routesData.value
  if (!d.length) return []
  const totalRecords = d.reduce((a, r) => a + r.total_records, 0)
  const totalTrips = d.reduce((a, r) => a + r.total_trips, 0)
  const avgTravel = d.reduce((a, r) => a + (r.avg_travel_time_seconds || 0), 0) / d.length
  const avgDwell = d.reduce((a, r) => a + (r.avg_dwell_time_seconds || 0), 0) / d.length
  return [
    { value: d.length, label: 'Active Routes' },
    { value: formatNum(totalRecords), label: 'Total Records' },
    { value: formatNum(totalTrips), label: 'Total Trips' },
    { value: avgTravel.toFixed(1) + 's', label: 'Avg Travel Time' }
  ]
})

const PALTTE = ['#10b981', '#f97316', '#ef4444', '#3b82f6', '#8b5cf6']

// Interactive Bar Chart
const barOption = computed(() => {
  const data = routesData.value
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#0f172a' },
      formatter: p => {
        const d = p[0]
        return `<b>${d.name}</b><br/>Records: ${Number(d.value).toLocaleString()}`
      }
    },
    grid: { left: 60, right: 30, top: 30, bottom: 50 },
    xAxis: {
      type: 'category',
      data: data.map(r => r.route_name),
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { color: '#64748b', fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: {
        color: '#64748b',
        formatter: v => v >= 1000000 ? (v / 1000000).toFixed(1) + 'M' : (v / 1000).toFixed(0) + 'K'
      }
    },
    series: [{
      type: 'bar',
      emphasis: { itemStyle: { shadowBlur: 18, shadowColor: 'rgba(0,0,0,0.28)', shadowOffsetY: 3 } },
      data: data.map((r, i) => ({
        value: r.total_records,
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: PALTTE[i] + 'dd' },
            { offset: 1, color: PALTTE[i] + '66' }
          ])
        }
      })),
      barWidth: '45%',
      label: {
        show: true,
        position: 'top',
        formatter: p => (p.value / 1000000).toFixed(1) + 'M',
        color: '#475569',
        fontSize: 11,
        fontWeight: 600
      },
      animationDelay: i => i * 80
    }]
  }
})

// Treemap
const treemapOption = computed(() => {
  const data = routesData.value
  return {
    tooltip: {
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#0f172a' },
      formatter: p => `<b>${p.name}</b><br/>Records: ${Number(p.value).toLocaleString()}`
    },
    series: [{
      type: 'treemap',
      data: data.map((r, i) => ({
        name: r.route_name,
        value: r.total_records,
        itemStyle: {
          color: PALTTE[i],
          borderColor: '#fff',
          borderWidth: 3,
          gapWidth: 2
        },
        label: {
          show: true,
          color: '#fff',
          fontWeight: 600,
          fontSize: 13,
          formatter: p => {
            const total = data.reduce((a, x) => a + x.total_records, 0)
            return `${p.name}\n${((p.value / total) * 100).toFixed(1)}%`
          }
        }
      })),
      roam: false,
      nodeClick: false,
      breadcrumb: { show: false },
      levels: [{ itemStyle: { borderWidth: 0 } }],
      animationDuration: 900,
      animationEasing: 'cubicOut'
    }]
  }
})

// Radar Chart
const radarOption = computed(() => {
  const data = routesData.value
  const maxRecords = Math.max(...data.map(r => r.total_records))
  const maxTrips = Math.max(...data.map(r => r.total_trips))
  const maxStops = Math.max(...data.map(r => r.total_stops))
  const maxTravel = Math.max(...data.map(r => r.avg_travel_time_seconds || 0))
  const maxDwell = Math.max(...data.map(r => r.avg_dwell_time_seconds || 0))
  const maxHeadway = Math.max(...data.map(r => r.avg_headway_trunk_seconds || 0))

  return {
    tooltip: {
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#0f172a' }
    },
    legend: {
      data: data.map(r => r.route_name),
      bottom: 0,
      textStyle: { color: '#64748b', fontSize: 12 },
      itemWidth: 12,
      itemHeight: 8
    },
    radar: {
      indicator: [
        { name: 'Records', max: maxRecords * 1.1 },
        { name: 'Trips', max: maxTrips * 1.1 },
        { name: 'Stops', max: maxStops * 1.1 },
        { name: 'Travel Time', max: maxTravel * 1.1 },
        { name: 'Dwell Time', max: maxDwell * 1.1 },
        { name: 'Headway', max: maxHeadway * 1.1 }
      ],
      splitArea: {
        areaStyle: {
          color: ['rgba(14,165,233,0.03)', 'rgba(14,165,233,0.06)']
        }
      },
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      splitLine: { lineStyle: { color: '#e2e8f0' } },
      axisName: { color: '#64748b', fontSize: 12 }
    },
    series: [{
      type: 'radar',
      data: data.map((r, i) => ({
        name: r.route_name,
        value: [
          r.total_records,
          r.total_trips,
          r.total_stops,
          r.avg_travel_time_seconds || 0,
          r.avg_dwell_time_seconds || 0,
          r.avg_headway_trunk_seconds || 0
        ],
        lineStyle: { width: 2, color: PALTTE[i] },
        areaStyle: {
          color: new echarts.graphic.RadialGradient(0.5, 0.5, 0.5, [
            { offset: 0, color: PALTTE[i] + '44' },
            { offset: 1, color: PALTTE[i] + '11' }
          ])
        },
        itemStyle: { color: PALTTE[i] }
      }))
    }]
  }
})

// Dwell time bar
const dwellOption = computed(() => {
  const data = [...routesData.value].sort((a, b) => a.avg_dwell_time_seconds - b.avg_dwell_time_seconds)
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 120, right: 30, top: 20, bottom: 30 },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9' } }, axisLabel: { color: '#64748b', formatter: '{value}s' } },
    yAxis: { type: 'category', data: data.map(r => r.route_name), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#475569' } },
    series: [{
      type: 'bar',
      emphasis: { itemStyle: { shadowBlur: 18, shadowColor: 'rgba(0,0,0,0.28)', shadowOffsetY: 3 } },
      data: data.map((r, i) => ({
        value: r.avg_dwell_time_seconds,
        itemStyle: {
          borderRadius: [0, 6, 6, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#10b981' },
            { offset: 1, color: '#34d399' }
          ])
        }
      })),
      barWidth: '40%',
      label: { show: true, position: 'right', formatter: '{c}s', color: '#475569', fontSize: 11 }
    }]
  }
})

const headwayOption = computed(() => {
  const data = [...routesData.value].sort((a, b) => (a.avg_headway_trunk_seconds || 0) - (b.avg_headway_trunk_seconds || 0))
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 120, right: 30, top: 20, bottom: 30 },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9' } }, axisLabel: { color: '#64748b', formatter: '{value}s' } },
    yAxis: { type: 'category', data: data.map(r => r.route_name), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#475569' } },
    series: [{
      type: 'bar',
      emphasis: { itemStyle: { shadowBlur: 18, shadowColor: 'rgba(0,0,0,0.28)', shadowOffsetY: 3 } },
      data: data.map(r => ({
        value: r.avg_headway_trunk_seconds || 0,
        itemStyle: {
          borderRadius: [0, 6, 6, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#0ea5e9' },
            { offset: 1, color: '#38bdf8' }
          ])
        }
      })),
      barWidth: '40%',
      label: { show: true, position: 'right', formatter: '{c}s', color: '#475569', fontSize: 11 }
    }]
  }
})
</script>

<style scoped>
.kpi-row {
  margin-bottom: 20px;
}
</style>
