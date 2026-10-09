<template>
  <div class="app">
    <aside id="app-sidebar" class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-brand">
        <span class="sidebar-brand-name">{{ t('nav.companyName') }}</span>
        <span class="sidebar-brand-subtitle">{{ t('nav.subtitle') }}</span>
      </div>
      <nav class="sidebar-nav" aria-label="Primary">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :title="t(item.labelKey)"
          class="sidebar-link"
          exact-active-class="active"
        >
          <svg
            class="sidebar-icon"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path v-for="d in item.icon" :key="d" :d="d" />
          </svg>
          <span class="sidebar-label">{{ t(item.labelKey) }}</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <LanguageSwitcher />
        <ProfileMenu
          @show-profile-details="showProfileDetails = true"
          @show-tasks="showTasks = true"
        />
      </div>
    </aside>
    <div v-if="sidebarOpen" class="sidebar-backdrop" @click="closeSidebar"></div>

    <div class="workspace">
      <header class="topbar">
        <button
          type="button"
          class="hamburger"
          :aria-label="t('nav.toggleMenu')"
          aria-controls="app-sidebar"
          :aria-expanded="sidebarOpen ? 'true' : 'false'"
          @click="toggleSidebar"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" aria-hidden="true">
            <path d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 class="topbar-title">{{ pageTitle }}</h1>
        <FilterBar />
      </header>
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const route = useRoute()
    const sidebarOpen = ref(false)
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Nav definition; icon is a list of SVG path 'd' strings drawn on a 24x24 viewBox
    const navItems = [
      { path: '/', labelKey: 'nav.overview', icon: ['M4 4h6v6H4z', 'M14 4h6v6h-6z', 'M4 14h6v6H4z', 'M14 14h6v6h-6z'] },
      { path: '/inventory', labelKey: 'nav.inventory', icon: ['M21 8l-9-5-9 5 9 5 9-5z', 'M3 8v8l9 5 9-5V8', 'M12 13v8'] },
      { path: '/orders', labelKey: 'nav.orders', icon: ['M9 4h6a1 1 0 011 1v1H8V5a1 1 0 011-1z', 'M8 6H6a1 1 0 00-1 1v13a1 1 0 001 1h12a1 1 0 001-1V7a1 1 0 00-1-1h-2', 'M9 12h6', 'M9 16h6'] },
      { path: '/spending', labelKey: 'nav.finance', icon: ['M12 3v18', 'M16 7.5c-.6-1-1.9-1.5-4-1.5-2.2 0-3.5.9-3.5 2.4 0 3.4 7.5 1.6 7.5 5.2 0 1.5-1.4 2.4-4 2.4-2 0-3.5-.6-4.2-1.8'] },
      { path: '/demand', labelKey: 'nav.demandForecast', icon: ['M3 17l6-6 4 4 8-8', 'M15 7h6v6'] },
      { path: '/reports', labelKey: 'nav.reports', icon: ['M5 20V10', 'M12 20V4', 'M19 20v-7', 'M3 20h18'] }
    ]

    const pageTitle = computed(() => {
      const item = navItems.find(i => i.path === route.path)
      return item ? t(item.labelKey) : t('nav.companyName')
    })

    const closeSidebar = () => { sidebarOpen.value = false }
    const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }

    // Close the mobile drawer after navigating
    watch(() => route.path, closeSidebar)

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      navItems,
      pageTitle,
      sidebarOpen,
      closeSidebar,
      toggleSidebar,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
:root {
  /* Spacing (4px scale) */
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
  --space-5: 20px; --space-6: 24px; --space-8: 32px; --space-10: 40px;

  /* Color */
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-surface-muted: #f1f5f9;
  --color-border: #e2e8f0;
  --color-border-strong: #cbd5e1;
  --color-text: #0f172a;
  --color-text-secondary: #334155;
  --color-text-muted: #64748b;
  --color-primary: #2563eb;
  --color-primary-soft: #eff6ff;
  --color-success: #059669;
  --color-warning: #ea580c;
  --color-danger: #dc2626;

  /* Sidebar */
  --sidebar-bg: #0f172a;
  --sidebar-text: #cbd5e1;
  --sidebar-text-muted: #64748b;
  --sidebar-hover-bg: rgba(255, 255, 255, 0.05);
  --sidebar-active-bg: rgba(255, 255, 255, 0.08);
  --sidebar-border: rgba(255, 255, 255, 0.08);

  /* Shape */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 12px;
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.06);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);

  /* Layout */
  --sidebar-width: 248px;
  --sidebar-width-collapsed: 72px;
  --topbar-height: 64px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app {
  min-height: 100vh;
}

/* Sidebar */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: var(--sidebar-width);
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  display: flex;
  flex-direction: column;
  z-index: 60;
  transition: transform 0.2s ease, width 0.2s ease;
}

.sidebar-brand {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-6) var(--space-5);
  border-bottom: 1px solid var(--sidebar-border);
}

.sidebar-brand-name {
  font-size: 1.125rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.025em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-brand-subtitle {
  font-size: 0.75rem;
  color: var(--sidebar-text-muted);
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-4) var(--space-3);
  overflow-y: auto;
}

.sidebar-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  min-height: 40px;
  border-radius: var(--radius-sm);
  color: var(--sidebar-text);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.sidebar-link:hover {
  background: var(--sidebar-hover-bg);
  color: #ffffff;
}

.sidebar-link.active {
  background: var(--sidebar-active-bg);
  color: #ffffff;
}

/* 3px accent bar flush with the sidebar's left edge (nav has --space-3 padding) */
.sidebar-link.active::before {
  content: '';
  position: absolute;
  left: calc(var(--space-3) * -1);
  top: var(--space-2);
  bottom: var(--space-2);
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--color-primary);
}

.sidebar-icon {
  flex-shrink: 0;
}

.sidebar-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3);
  border-top: 1px solid var(--sidebar-border);
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  /* Between topbar (50) and sidebar (60): dims the page but not the open drawer */
  z-index: 55;
}

/* Workspace */
.workspace {
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.2s ease;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-4);
  min-height: var(--topbar-height);
  padding: var(--space-2) var(--space-8);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.topbar-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
  margin-right: auto;
}

.hamburger {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  cursor: pointer;
}

.hamburger:hover {
  background: var(--color-surface-muted);
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  padding: var(--space-8);
}

/* Collapsed icon rail */
@media (max-width: 1024px) and (min-width: 769px) {
  .sidebar {
    width: var(--sidebar-width-collapsed);
  }

  .workspace {
    margin-left: var(--sidebar-width-collapsed);
  }

  .sidebar-brand {
    align-items: center;
    padding: var(--space-6) var(--space-2);
  }

  .sidebar-brand-subtitle,
  .sidebar-label {
    display: none;
  }

  .sidebar-brand-name {
    font-size: 0.75rem;
    max-width: 100%;
  }

  .sidebar-link {
    justify-content: center;
    padding: var(--space-2);
  }

  .sidebar-footer {
    align-items: center;
  }
}

/* Off-canvas drawer */
@media (max-width: 768px) {
  .sidebar {
    width: var(--sidebar-width);
    transform: translateX(-100%);
    /* Hide the closed drawer from keyboard/screen readers; delay so the slide-out still animates */
    visibility: hidden;
    transition: transform 0.2s ease, visibility 0s linear 0.2s;
  }

  .sidebar.open {
    transform: translateX(0);
    visibility: visible;
    transition: transform 0.2s ease, visibility 0s;
  }

  .workspace {
    margin-left: 0;
  }

  .hamburger {
    display: inline-flex;
  }

  .topbar {
    padding: var(--space-2) var(--space-4);
  }

  .topbar-title {
    margin-right: 0;
    flex: 1;
  }

  .main-content {
    padding: var(--space-4);
  }
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-header h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--space-2);
  letter-spacing: -0.025em;
}

.page-header p {
  color: var(--color-text-muted);
  font-size: 0.938rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--color-surface);
  padding: var(--space-6);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-md);
}

.stat-label {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-2);
}

.stat-value {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
}

.stat-card.warning .stat-value {
  color: var(--color-warning);
}

.stat-card.success .stat-value {
  color: var(--color-success);
}

.stat-card.danger .stat-value {
  color: var(--color-danger);
}

.stat-card.info .stat-value {
  color: var(--color-primary);
}

.card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--color-bg);
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

th {
  text-align: left;
  padding: var(--space-3) var(--space-4);
  font-weight: 600;
  color: var(--color-text-secondary);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-surface-muted);
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: var(--color-bg);
}

.badge {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge.success {
  background: #d1fae5;
  color: #065f46;
}

.badge.warning {
  background: #fed7aa;
  color: #92400e;
}

.badge.danger {
  background: #fecaca;
  color: #991b1b;
}

.badge.info {
  background: #dbeafe;
  color: #1e40af;
}

.badge.increasing {
  background: #d1fae5;
  color: #065f46;
}

.badge.decreasing {
  background: #fecaca;
  color: #991b1b;
}

.badge.stable {
  background: #e0e7ff;
  color: #3730a3;
}

.badge.high {
  background: #fecaca;
  color: #991b1b;
}

.badge.medium {
  background: #fed7aa;
  color: #92400e;
}

.badge.low {
  background: #dbeafe;
  color: #1e40af;
}

.loading {
  text-align: center;
  padding: var(--space-10);
  color: var(--color-text-muted);
  font-size: 0.938rem;
}

.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
  font-size: 0.938rem;
}
</style>
