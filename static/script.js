const video = document.getElementById('video');
const captureButton = document.getElementById('capture');

navigator.mediaDevices.getUserMedia({ video: true, audio: false })
 .then(stream => {
    video.srcObject = stream;
  })
 .catch(error => {
    console.error('Error accessing media devices.', error);
  });

captureButton.addEventListener('click', async () => {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  const imgData = canvas.toDataURL('image/png');

  try {
    const response = await fetch('/upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ image: imgData })
    });

    if (response.ok) {
      console.log('Image uploaded successfully');
    } else {
      console.error('Failed to upload image');
    }
  } catch (error) {
    console.error('Error uploading image.', error);
  }
});