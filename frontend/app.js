// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCpcmfgcmfuXRizJlrMcb4yEKQwxFgfd4s",
  authDomain: "pressure-watcher-ea41a.firebaseapp.com",
  projectId: "pressure-watcher-ea41a",
  storageBucket: "pressure-watcher-ea41a.firebasestorage.app",
  messagingSenderId: "660910236769",
  appId: "1:660910236769:web:b0d1f02251db09341db620"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// DOM elements
const gaugeImage = document.getElementById('gaugeImage');
const noImagePlaceholder = document.getElementById('noImagePlaceholder');
const pressureValue = document.getElementById('pressureValue');
const timestamp = document.getElementById('timestamp');
const status = document.getElementById('status');
const historyContainer = document.getElementById('historyContainer');

/**
 * Update the current reading display
 */
function updateCurrentReading(data) {
    // Update pressure value
    pressureValue.textContent = data.pressure.toFixed(2);

    // Update timestamp
    const date = new Date(data.timestamp);
    timestamp.textContent = date.toLocaleString();

    // Update image
    if (data.image) {
        gaugeImage.src = `data:image/jpeg;base64,${data.image}`;
        gaugeImage.classList.add('visible');
        noImagePlaceholder.style.display = 'none';
    }

    // Update status
    status.textContent = 'Active';
    status.className = 'value status-indicator active';
}

/**
 * Listen to Firestore for real-time updates
 */
function listenToFirestore() {
    /*
    // Uncomment when Firebase is configured
    const q = query(
        collection(db, 'readings'),
        orderBy('timestamp', 'desc'),
        limit(20)
    );

    onSnapshot(q, (snapshot) => {
        const readings = [];
        snapshot.forEach((doc) => {
            readings.push({ id: doc.id, ...doc.data() });
        });

        // Update history display
        updateHistory(readings);

        // Update current reading with the latest
        if (readings.length > 0) {
            const latest = readings[0];
            pressureValue.textContent = latest.pressure.toFixed(2);
            const date = new Date(latest.timestamp);
            timestamp.textContent = date.toLocaleString();
        }
    });
    */
}

/**
 * Update history display
 */
function updateHistory(readings) {
    if (readings.length === 0) {
        historyContainer.innerHTML = '<p class="placeholder">No readings yet</p>';
        return;
    }

    historyContainer.innerHTML = readings.map(reading => {
        const date = new Date(reading.timestamp);
        return `
            <div class="history-item">
                <span class="history-time">${date.toLocaleString()}</span>
                <span class="history-pressure">${reading.pressure.toFixed(2)} PSI</span>
            </div>
        `;
    }).join('');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Pressure Watcher initialized');

    // Set initial status
    status.textContent = 'Waiting';
    status.className = 'value status-indicator waiting';

    // Start listening to Firestore
    listenToFirestore();
});
