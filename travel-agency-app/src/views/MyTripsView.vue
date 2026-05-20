<script setup>
import { computed, onMounted, ref } from 'vue'
import { tenantConfig } from '../config/tenantConfig.js'
import { bookingService } from '../services/bookingService.js'
import { useAuth } from '../composables/useAuth.js'

const { userId, userEmail } = useAuth()

const isLoading = ref(true)
const errorMessage = ref('')
const trips = ref([])

function formatDate(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value || 'N/A'
  return date.toLocaleDateString('en-GB', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const tripCountLabel = computed(() => {
  const tripCount = trips.value.length
  return tripCount === 1 ? '1 saved trip' : `${tripCount} saved trips`
})

async function loadTrips() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    trips.value = await bookingService.getUserBookings(userId.value)
  } catch (error) {
    errorMessage.value = error.message || 'Unable to load saved trips.'
    trips.value = []
  } finally {
    isLoading.value = false
  }
}

async function handleCancel(bookingId) {
  if (!window.confirm("Are you sure you want to cancel this trip? This will permanently delete all associated reservations.")) {
    return
  }

  try {
    await bookingService.cancelBooking(bookingId)
    trips.value = trips.value.filter(trip => trip.bookingId !== bookingId)
  } catch (error) {
    alert(error.message || "Failed to cancel trip. Please try again.")
  }
}

const editingTripId = ref(null)
const editStartDate = ref('')
const editEndDate = ref('')

function startEdit(trip) {
  editingTripId.value = trip.bookingId
  
  // Format dates to YYYY-MM-DD for input value
  const sDate = new Date(trip.startDate)
  const eDate = new Date(trip.endDate)
  
  editStartDate.value = !Number.isNaN(sDate.getTime()) 
    ? sDate.toISOString().split('T')[0] 
    : trip.startDate
  editEndDate.value = !Number.isNaN(eDate.getTime()) 
    ? eDate.toISOString().split('T')[0] 
    : trip.endDate
}

function cancelEdit() {
  editingTripId.value = null
  editStartDate.value = ''
  editEndDate.value = ''
}

async function handleSaveEdit(bookingId) {
  if (!editStartDate.value || !editEndDate.value) {
    alert("Please enter valid start and end dates.")
    return
  }

  try {
    const updated = await bookingService.updateBooking(bookingId, {
      startDate: editStartDate.value,
      endDate: editEndDate.value
    })
    
    const index = trips.value.findIndex(trip => trip.bookingId === bookingId)
    if (index !== -1) {
      trips.value[index].startDate = updated.startDate || updated.Start_Date || editStartDate.value
      trips.value[index].endDate = updated.endDate || updated.End_Date || editEndDate.value
    }
    
    cancelEdit()
  } catch (error) {
    alert(error.message || "Failed to update booking. Please try again.")
  }
}

onMounted(() => {
  loadTrips()
})
</script>

<template>
  <div class="my-trips-view">
    <div class="my-trips-view__hero">
      <div>
        <p class="my-trips-view__eyebrow">Agent {{ tenantConfig.agentId }}</p>
        <h1 class="my-trips-view__title">My Trips</h1>
        <p class="my-trips-view__sub">
          Saved trips for {{ userEmail || `User ${userId}` }} with {{ tenantConfig.brandName }}.
        </p>
      </div>
      <div class="my-trips-view__summary">{{ tripCountLabel }}</div>
    </div>

    <div v-if="isLoading" class="state-card">Loading saved trips...</div>
    <div v-else-if="errorMessage" class="state-card state-card--error">{{ errorMessage }}</div>
    <div v-else-if="trips.length === 0" class="state-card">No saved trips found for this user and agent.</div>

    <div v-else class="trips-list">
      <article v-for="trip in trips" :key="trip.bookingId" class="trip-card">
        <div v-if="editingTripId === trip.bookingId" class="trip-card__header trip-card__header--edit">
          <div>
            <p class="trip-card__meta">Editing Booking #{{ trip.bookingId }}</p>
            <div class="edit-fields">
              <label class="edit-label">
                Start:
                <input type="date" v-model="editStartDate" class="edit-input" />
              </label>
              <label class="edit-label">
                End:
                <input type="date" v-model="editEndDate" class="edit-input" />
              </label>
            </div>
          </div>
          <div class="trip-card__actions">
            <button class="btn-save-trip" @click="handleSaveEdit(trip.bookingId)" title="Save changes">
              💾 Save
            </button>
            <button class="btn-cancel-edit" @click="cancelEdit" title="Cancel editing">
              Cancel
            </button>
          </div>
        </div>
        <div v-else class="trip-card__header">
          <div>
            <p class="trip-card__meta">Booking #{{ trip.bookingId }}</p>
            <h2 class="trip-card__title">{{ formatDate(trip.startDate) }} to {{ formatDate(trip.endDate) }}</h2>
          </div>
          <div class="trip-card__actions">
            <button class="btn-edit-trip" @click="startEdit(trip)" title="Edit trip dates">
              ✏️ Edit Dates
            </button>
            <button class="btn-cancel-trip" @click="handleCancel(trip.bookingId)" title="Cancel this trip">
              ❌ Cancel Trip
            </button>
            <div class="trip-card__pill">{{ trip.flightReservations.length }} flights · {{ trip.hotelReservations.length }} hotels</div>
          </div>
        </div>

        <section class="trip-section">
          <h3 class="trip-section__title">Flight Details</h3>
          <p v-if="trip.flightReservations.length === 0" class="trip-section__empty">No flights saved for this trip.</p>
          <div v-else class="reservation-grid">
            <div v-for="flight in trip.flightReservations" :key="`${trip.bookingId}-${flight.Reservation_No}`" class="reservation-card">
              <div class="reservation-card__title">Flight Reservation</div>
              <div><strong>Airline code:</strong> {{ flight.Airline_Code || 'N/A' }}</div>
              <div><strong>Flight number:</strong> {{ flight.Flight_Number || 'N/A' }}</div>
              <div>{{ flight.Origin_Airport_Code }} to {{ flight.Destination_Airport_Code }}</div>
              <div>Departure: {{ formatDate(flight.Departure_Date) }} {{ flight.Departure_Time }}</div>
              <div>Arrival: {{ formatDate(flight.Arrive_Date) }} {{ flight.Arrive_Time }}</div>
              <div>Rate: ${{ Number(flight.Rate || 0).toLocaleString() }}</div>
            </div>
          </div>
        </section>

        <section class="trip-section">
          <h3 class="trip-section__title">Hotel Details</h3>
          <p v-if="trip.hotelReservations.length === 0" class="trip-section__empty">No hotel saved for this trip.</p>
          <div v-else class="reservation-grid">
            <div v-for="hotel in trip.hotelReservations" :key="`${trip.bookingId}-${hotel.Reservation_No}`" class="reservation-card">
              <div class="reservation-card__title">Hotel Reservation</div>
              <div><strong>Hotel Name:</strong> {{ hotel.Hotel_Name || 'Hotel name unavailable' }}</div>
              <div>Check in: {{ formatDate(hotel.Check_In_Date) }} {{ hotel.Check_In_Time }}</div>
              <div>Check out: {{ formatDate(hotel.Check_Out_Date) }} {{ hotel.Check_Out_Time }}</div>
              <div>Rate: ${{ Number(hotel.Rate || 0).toLocaleString() }}</div>
            </div>
          </div>
        </section>
      </article>
    </div>
  </div>
</template>

<style scoped>
.my-trips-view {
  min-height: calc(100vh - 56px);
  background: var(--color-bg);
  padding: 2rem;
}

.my-trips-view__hero {
  max-width: 1200px;
  margin: 0 auto 1.5rem;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
}

.my-trips-view__eyebrow {
  margin: 0 0 0.35rem;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-accent-dark);
}

.my-trips-view__title {
  margin: 0;
  font-size: 2rem;
  color: var(--color-primary-dark);
}

.my-trips-view__sub {
  margin: 0.5rem 0 0;
  color: var(--color-text-muted);
}

.my-trips-view__summary {
  padding: 0.6rem 0.9rem;
  border-radius: 999px;
  background: #fff;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  font-weight: 700;
}

.state-card {
  max-width: 1200px;
  margin: 0 auto;
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 2rem;
  color: var(--color-text-muted);
}

.state-card--error {
  color: #c0392b;
}

.trips-list {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.trip-card {
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: 18px;
  padding: 1.5rem;
  box-shadow: 0 10px 24px rgba(26, 54, 93, 0.06);
}

.trip-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.trip-card__meta {
  margin: 0 0 0.35rem;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.trip-card__title {
  margin: 0;
  color: var(--color-primary-dark);
  font-size: 1.2rem;
}

.trip-card__pill {
  padding: 0.45rem 0.75rem;
  border-radius: 999px;
  background: var(--color-primary-bg);
  color: var(--color-primary-dark);
  font-size: 0.85rem;
  font-weight: 700;
  white-space: nowrap;
}

.trip-section + .trip-section {
  margin-top: 1.25rem;
}

.trip-section__title {
  margin: 0 0 0.75rem;
  color: var(--color-text);
  font-size: 1rem;
}

.trip-section__empty {
  margin: 0;
  color: var(--color-text-muted);
}

.reservation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.75rem;
}

.reservation-card {
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 1rem;
  background: #fcfdff;
  color: var(--color-text);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.reservation-card__title {
  font-weight: 700;
  color: var(--color-primary-dark);
}

.trip-card__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-cancel-trip {
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.btn-cancel-trip:hover {
  background: #b91c1c;
  color: #fff;
  border-color: #b91c1c;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(185, 28, 28, 0.15);
}

.btn-cancel-trip:active {
  transform: translateY(0);
}

.btn-edit-trip {
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  background: var(--color-bg-alt, #f3f4f6);
  color: var(--color-primary-dark, #4b5563);
  border: 1px solid var(--color-border, #d1d5db);
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.btn-edit-trip:hover {
  background: var(--color-primary-dark, #4b5563);
  color: #fff;
  border-color: var(--color-primary-dark, #4b5563);
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(75, 85, 99, 0.15);
}

.btn-edit-trip:active {
  transform: translateY(0);
}

.btn-save-trip {
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  background: #10b981;
  color: #fff;
  border: 1px solid #059669;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.btn-save-trip:hover {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(5, 150, 105, 0.2);
}

.btn-save-trip:active {
  transform: translateY(0);
}

.btn-cancel-edit {
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  background: #f3f4f6;
  color: #4b5563;
  border: 1px solid #d1d5db;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  display: inline-flex;
  align-items: center;
}

.btn-cancel-edit:hover {
  background: #e5e7eb;
}

.edit-fields {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.edit-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-text-muted, #6b7280);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.edit-input {
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 8px;
  padding: 0.25rem 0.5rem;
  font-size: 0.85rem;
  font-family: inherit;
  outline: none;
  background: #fff;
  color: var(--color-text);
}

.edit-input:focus {
  border-color: var(--color-accent-dark, #3b82f6);
}

@media (max-width: 768px) {
  .my-trips-view {
    padding: 1rem;
  }

  .my-trips-view__hero,
  .trip-card__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .trip-card__actions {
    margin-top: 0.75rem;
    width: 100%;
    justify-content: space-between;
  }
}
</style>