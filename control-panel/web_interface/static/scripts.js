document.addEventListener("DOMContentLoaded", async () => {
    const slider = document.getElementById("slider");
    const viewer = document.getElementById("section-viewer");

    // Fetch image URLs from the server
    const response = await fetch("/images");
    const images = await response.json();

    console.log("Fetched images:", images); // Check if URLs are correct

    if (images.length > 0) {
        // Initialize slider and first image
        slider.max = images.length - 1;
        viewer.src = images[0];
        console.log("Initial image set to:", images[0]);
    } else {
        console.error("No images found!");
        return;
    }

    // Update image on slider input
    slider.addEventListener("input", () => {
        const index = slider.value;
        console.log("Slider moved to index:", index, "Image:", images[index]);

        viewer.style.opacity = "0"; // Smooth fade-out
        setTimeout(() => {
            viewer.src = images[index]; // Update the image
            viewer.style.opacity = "1"; // Smooth fade-in
        }, 200);
    });
});