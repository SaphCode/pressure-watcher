/**
 * Test utilities for Pressure Watcher backend
 */

const resultDiv = document.getElementById('result');

/**
 * Display result in the UI
 */
function displayResult(message, type = 'info') {
    const className = type === 'error' ? 'result error' : type === 'success' ? 'result success' : 'result';
    resultDiv.className = className;
    resultDiv.innerHTML = message;
}

/**
 * Create a simple test image
 */
function createDummyImage() {
    return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        canvas.width = 640;
        canvas.height = 480;
        const ctx = canvas.getContext('2d');

        // Simple solid color
        ctx.fillStyle = '#4a5568';
        ctx.fillRect(0, 0, 640, 480);

        ctx.fillStyle = 'white';
        ctx.font = '30px Arial';
        ctx.fillText('Test Image', 250, 240);

        canvas.toBlob((blob) => {
            resolve(blob);
        }, 'image/jpeg', 0.9);
    });
}

/**
 * Upload image to backend
 */
async function uploadImage(imageBlob) {
    const apiUrl = document.getElementById('apiUrl').value;

    displayResult('Uploading image...', 'info');

    try {
        const formData = new FormData();
        formData.append('file', imageBlob, 'test-image.jpg');

        const response = await fetch(`${apiUrl}/upload-image`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Display success result
        let resultHTML = '<h3>Upload Successful!</h3>';
        resultHTML += `<p><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}</p>`;
        resultHTML += `<p><strong>Pressure Reading:</strong> ${data.pressure} PSI</p>`;
        resultHTML += `<p><strong>Status:</strong> ${data.status}</p>`;

        if (data.image) {
            resultHTML += '<h4>Image Received:</h4>';
            resultHTML += `<img src="data:image/jpeg;base64,${data.image}" class="image-preview" alt="Received image">`;
        }

        displayResult(resultHTML, 'success');

    } catch (error) {
        displayResult(`<h3>Upload Failed</h3><p>${error.message}</p>`, 'error');
    }
}

/**
 * Test with dummy image
 */
async function testWithDummyImage() {
    try {
        const imageBlob = await createDummyImage();
        await uploadImage(imageBlob);
    } catch (error) {
        displayResult(`<h3>Error Creating Dummy Image</h3><p>${error.message}</p>`, 'error');
    }
}

/**
 * Test with real image file
 */
async function testWithRealImage(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];

        // Validate it's an image
        if (!file.type.startsWith('image/')) {
            displayResult('<h3>Error</h3><p>Please select a valid image file</p>', 'error');
            return;
        }

        await uploadImage(file);
    }
}
