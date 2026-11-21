<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <div class="logo">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
          </svg>
          <div>
            <h1>MBTA Subway Analytics</h1>
            <span>2026 Performance Dashboard</span>
          </div>
        </div>
        <el-menu
          mode="horizontal"
          :ellipsis="false"
          router
          :default-active="$route.path"
          class="nav-menu"
        >
          <el-menu-item index="/peak">
            <el-icon><Clock /></el-icon>Peak vs Off-Peak Analysis
          </el-menu-item>
          <el-menu-item index="/station">
            <el-icon><Location /></el-icon>Station Efficiency Analysis
          </el-menu-item>
          <el-menu-item index="/route">
            <el-icon><TrendCharts /></el-icon>Route Performance Analysis
          </el-menu-item>
        </el-menu>
      </div>
    </el-header>

    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <el-footer class="app-footer">
      <span>Zhaohan Hou · Jiaxin Wang · UNC DATA707</span>
    </el-footer>
  </el-container>
</template>

<script setup>
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}

.app-header {
  background: #e5f3f1;
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(14, 165, 233, 0.12);
  padding: 0;
  height: auto;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1440px;
  margin: 0 auto;
  padding: 14px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--primary);
}

.logo h1 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.2;
}

.logo span {
  font-size: 12px;
  color: var(--text-muted);
}

.logo > div {
  display: flex;
  flex-direction: column;
}

.nav-menu {
  flex: none;
  background: transparent !important;
  border: none !important;
  width: max-content;
  white-space: nowrap;
}

/* 禁用 Element Plus horizontal 菜单的溢出折叠 */
.nav-menu .el-menu-item,
.nav-menu .el-sub-menu {
  display: inline-flex !important;
  visibility: visible !important;
  opacity: 1 !important;
}

/* 隐藏自动生成的 "more" 溢出按钮 */
.nav-menu > .el-sub-menu.is-more {
  display: none !important;
}

.nav-menu .el-menu-item {
  font-weight: 500;
  font-size: 14px;
  white-space: nowrap;
}

.app-main {
  max-width: 1440px;
  margin: 0 auto;
  padding: 28px;
  width: 100%;
}

.app-footer {
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: var(--text-muted);
  border-top: 1px solid rgba(14, 165, 233, 0.1);
  background: #e5f3f1;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from { opacity: 0; transform: translateY(8px); }
.fade-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
