<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  activities: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  error: { type: String, default: null },
  selectedActivities: { type: Array, default: () => [] },
})

const emit = defineEmits(['toggle-activity'])

const filterType = ref('ALL') // 'ALL' or 'FREE'

const filteredActivities = computed(() => {
  if (filterType.value === 'FREE') {
    return props.activities.filter(act => act.pricePerPerson === 0 || act.priceType === 'Free')
  }
  return props.activities
})

function isSelected(activityId) {
  return props.selectedActivities.some(a => a.id === activityId)
}
</script>

<template>
  <div class="panel-content">
    <div class="filter-bar">
      <span class="filter-label">🎯 Filter Activities:</span>
      <div class="filter-options">
        <button
          class="filter-btn"
          :class="{ 'filter-btn--active': filterType === 'ALL' }"
          @click="filterType = 'ALL'"
        >
          All Activities
        </button>
        <button
          class="filter-btn"
          :class="{ 'filter-btn--active': filterType === 'FREE' }"
          @click="filterType = 'FREE'"
        >
          Free & PWYW Tours
        </button>
      </div>
    </div>

    <template v-if="loading">
      <div v-for="n in 5" :key="n" class="card skeleton" />
    </template>

    <div v-else-if="error" class="state-message state-message--error">
      <span class="state-icon">⚠️</span>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="filteredActivities.length === 0" class="state-message">
      <span class="state-icon">🎯</span>
      <p>No activities match the selected filter.</p>
    </div>

    <div
      v-for="activity in filteredActivities"
      :key="activity.id"
      class="card activity-card"
      :class="{ 'card--selected': isSelected(activity.id) }"
      @click="emit('toggle-activity', activity)"
    >
      <div class="activity-card__icon">{{ activity.icon || '🎯' }}</div>

      <div class="activity-card__body">
        <div class="activity-card__top">
          <div>
            <div class="activity-name">{{ activity.name }}</div>
            <div class="activity-meta">
              <span class="category-badge">{{ activity.category }}</span>
              <span class="meta-dot">·</span>
              <span class="meta-text">⏱ {{ activity.duration }}</span>
              <span class="meta-dot">·</span>
              <span class="meta-text">⭐ {{ activity.rating }} ({{ activity.reviews }})</span>
            </div>
            <div class="activity-desc">{{ activity.description }}</div>
          </div>
          <div class="activity-price-block">
            <span class="price">{{ activity.pricePerPerson === 0 ? 'FREE' : '$' + activity.pricePerPerson }}</span>
            <span class="price-sub" v-if="activity.pricePerPerson > 0">/person</span>
            <div class="price-total" v-if="activity.pricePerPerson > 0">${{ activity.totalPrice.toLocaleString() }} total</div>
            <div class="price-total" v-else>Pay what you want</div>
            
            <button
              class="btn-select"
              :class="{ 'btn-select--selected': isSelected(activity.id) }"
            >
              {{ isSelected(activity.id) ? '✓ Added' : '+ Add' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  border: 1.5px solid var(--color-border);
  margin-bottom: 0.25rem;
}

.filter-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-text);
}

.filter-options {
  display: flex;
  gap: 0.5rem;
}

.filter-btn {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  border: 1.5px solid var(--color-border);
  background: #fff;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.filter-btn:hover {
  border-color: var(--color-primary-light);
  color: var(--color-text);
}

.filter-btn--active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff !important;
}

.card {
  background: #fff;
  border: 1.5px solid var(--color-border);
  border-radius: 12px;
  transition: border-color 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  cursor: pointer;
}

.card:hover {
  border-color: var(--color-primary-light);
  box-shadow: 0 4px 16px rgba(26, 54, 93, 0.1);
}

.card--selected {
  border-color: var(--color-primary) !important;
  background: var(--color-primary-bg);
}

.skeleton {
  height: 90px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  cursor: default;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.state-message {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text-muted);
}

.state-message--error { color: #c0392b; }

.state-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.5rem;
}

.activity-card__icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.activity-card__body {
  flex: 1;
}

.activity-card__top {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}

.activity-name {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--color-text);
  margin-bottom: 3px;
}

.activity-meta {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  flex-wrap: wrap;
  margin-bottom: 4px;
}

.category-badge {
  font-size: 0.68rem;
  background: #ede9fe;
  color: #5b21b6;
  padding: 2px 7px;
  border-radius: 20px;
  font-weight: 600;
}

.meta-dot {
  color: var(--color-border-dark);
  font-size: 0.75rem;
}

.meta-text {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.activity-desc {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  line-height: 1.4;
}

.activity-price-block {
  text-align: right;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  min-height: 80px;
}

.price {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-primary);
}

.price-sub {
  font-size: 0.72rem;
  color: var(--color-text-muted);
}

.price-total {
  font-size: 0.78rem;
  color: var(--color-text);
  font-weight: 600;
  margin-top: 2px;
}

.btn-select {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.35rem 0.85rem;
  border-radius: 6px;
  border: 1.5px solid var(--color-primary);
  background: #fff;
  color: var(--color-primary);
  cursor: pointer;
  margin-top: 0.5rem;
  transition: all 0.15s;
}

.btn-select:hover {
  background: var(--color-primary-bg);
}

.btn-select--selected {
  background: var(--color-primary) !important;
  color: #fff !important;
  border-color: var(--color-primary) !important;
}
</style>
