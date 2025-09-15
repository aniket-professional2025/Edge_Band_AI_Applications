// MODIFIED JAVA SCRIPT CODE FOR COLOR PICKER
document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const promptInput = document.getElementById('prompt');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const colorPickerSection = document.getElementById('color-picker-section');
    const selectedColorDiv = document.getElementById('selected-color');
    const colorValueDiv = document.getElementById('color-value');
    const schemeContainers = {
        monochromatic: document.querySelector('#monochromatic .scheme-colors'),
        analogous: document.querySelector('#analogous .scheme-colors'),
        complementary: document.querySelector('#complementary .scheme-colors'),
        triadic: document.querySelector('#triadic .scheme-colors')
    };

    generateBtn.addEventListener('click', function() {
        const prompt = promptInput.value.trim();

        if (!prompt) {
            alert('Please enter a prompt');
            return;
        }

        // Show loading message
        loadingDiv.classList.remove('hidden');
        resultDiv.innerHTML = '';
        colorPickerSection.classList.add('hidden');

        // Send request to server
        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'prompt': prompt
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading message
            loadingDiv.classList.add('hidden');

            // Display the image
            if (data.image) {
                resultDiv.innerHTML = `<img src="${data.image}" alt="Generated image">`;
                colorPickerSection.classList.remove('hidden');

                // Set up color picker on the image
                setupColorPicker(data.image);
            } else {
                resultDiv.innerHTML = '<p>Error generating image. Please try again.</p>';
            }
        })
        .catch(error => {
            loadingDiv.classList.add('hidden');
            resultDiv.innerHTML = '<p>Error generating image. Please try again.</p>';
            console.error('Error:', error);
        });
    });

    function setupColorPicker(imageUrl) {
        const img = document.querySelector('#result img');

        // Create a canvas to get pixel data
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const tempImg = new Image();

        tempImg.crossOrigin = 'Anonymous';
        tempImg.src = imageUrl;

        tempImg.onload = function() {
            canvas.width = tempImg.width;
            canvas.height = tempImg.height;
            ctx.drawImage(tempImg, 0, 0, tempImg.width, tempImg.height);

            img.addEventListener('click', function(event) {
                // Get click position relative to image
                const rect = img.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;

                // Scale coordinates to image size
                const scaleX = tempImg.width / rect.width;
                const scaleY = tempImg.height / rect.height;

                const pixelX = Math.floor(x * scaleX);
                const pixelY = Math.floor(y * scaleY);

                // Get pixel data
                const pixel = ctx.getImageData(pixelX, pixelY, 1, 1).data;
                const rgb = `rgb(${pixel[0]}, ${pixel[1]}, ${pixel[2]})`;

                // Display selected color
                selectedColorDiv.style.backgroundColor = rgb;
                colorValueDiv.textContent = `RGB: ${pixel[0]}, ${pixel[1]}, ${pixel[2]}`;

                // Generate color schemes
                generateColorSchemes(pixel[0], pixel[1], pixel[2]);
            });
        };
    }

    function generateColorSchemes(r, g, b) {
        // Convert RGB to HSL for easier color manipulation
        const hsl = rgbToHsl(r, g, b);
        const h = hsl[0], s = hsl[1], l = hsl[2];

        // Monochromatic scheme (different shades)
        const monoColors = [];
        for (let i = -2; i <= 2; i++) {
            const newL = Math.min(100, Math.max(0, l + i * 10));
            monoColors.push(hslToRgb(h, s, newL));
        }
        renderScheme(schemeContainers.monochromatic, monoColors);

        // Analogous scheme (colors adjacent on color wheel)
        const analogousColors = [
            hslToRgb((h + 30) % 360, s, l),
            hslToRgb((h + 15) % 360, s, l),
            [r, g, b],
            hslToRgb((h - 15 + 360) % 360, s, l),
            hslToRgb((h - 30 + 360) % 360, s, l)
        ];
        renderScheme(schemeContainers.analogous, analogousColors);

        // Complementary scheme (opposite color)
        const complementaryColors = [
            [r, g, b],
            hslToRgb((h + 180) % 360, s, l)
        ];
        renderScheme(schemeContainers.complementary, complementaryColors);

        // Triadic scheme (three colors evenly spaced)
        const triadicColors = [
            [r, g, b],
            hslToRgb((h + 120) % 360, s, l),
            hslToRgb((h + 240) % 360, s, l)
        ];
        renderScheme(schemeContainers.triadic, triadicColors);
    }

    function renderScheme(container, colors) {
        container.innerHTML = '';
        colors.forEach(color => {
            const colorDiv = document.createElement('div');
            colorDiv.style.backgroundColor = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
            container.appendChild(colorDiv);
        });
    }

    // Helper functions for color conversion
    function rgbToHsl(r, g, b) {
        r /= 255, g /= 255, b /= 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if (max === min) {
            h = s = 0; // achromatic
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                case g: h = (b - r) / d + 2; break;
                case b: h = (r - g) / d + 4; break;
            }
            h *= 60;
        }

        return [Math.round(h), Math.round(s * 100), Math.round(l * 100)];
    }

    function hslToRgb(h, s, l) {
        h /= 360;
        s /= 100;
        l /= 100;
        let r, g, b;

        if (s === 0) {
            r = g = b = l; // achromatic
        } else {
            const hue2rgb = (p, q, t) => {
                if (t < 0) t += 1;
                if (t > 1) t -= 1;
                if (t < 1/6) return p + (q - p) * 6 * t;
                if (t < 1/2) return q;
                if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                return p;
            };

            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;
            r = hue2rgb(p, q, h + 1/3);
            g = hue2rgb(p, q, h);
            b = hue2rgb(p, q, h - 1/3);
        }

        return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
    }
});

// Color pallate selection from pen.io
document.addEventListener('DOMContentLoaded', function () {
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const placeholderContent = document.getElementById('placeholderContent');
    const colorsContainer = document.getElementById('colorsContainer');
    const colorFormat = document.getElementById('colorFormat');
    const notification = document.getElementById('notification');
    const themeToggle = document.getElementById('themeToggle');
    const colorThief = new ColorThief();
    let extractedColors = [];

const colorNames = {
    '#FF0000': 'Red',
    '#8B0000': 'Dark Red',
    '#DC143C': 'Crimson',
    '#CD5C5C': 'Indian Red',
    '#FF4500': 'Orange Red',
    '#FF6347': 'Tomato',
    '#FFA500': 'Orange',
    '#FF8C00': 'Dark Orange',
    '#FF7F50': 'Coral',
    '#FFFF00': 'Yellow',
    '#FFD700': 'Gold',
    '#F0E68C': 'Khaki',
    '#BDB76B': 'Dark Khaki',
    '#008000': 'Green',
    '#006400': 'Dark Green',
    '#00FF00': 'Lime',
    '#90EE90': 'Light Green',
    '#8FBC8F': 'Dark Sea Green',
    '#00FA9A': 'Medium Spring Green',
    '#00FF7F': 'Spring Green',
    '#2E8B57': 'Sea Green',
    '#66CDAA': 'Medium Aquamarine',
    '#3CB371': 'Medium Sea Green',
    '#7CFC00': 'Lawn Green',
    '#7FFF00': 'Chartreuse',
    '#ADFF2F': 'Green Yellow',
    '#0000FF': 'Blue',
    '#00008B': 'Dark Blue',
    '#4169E1': 'Royal Blue',
    '#1E90FF': 'Dodger Blue',
    '#00BFFF': 'Deep Sky Blue',
    '#87CEEB': 'Sky Blue',
    '#4682B4': 'Steel Blue',
    '#5F9EA0': 'Cadet Blue',
    '#B0C4DE': 'Light Steel Blue',
    '#ADD8E6': 'Light Blue',
    '#800080': 'Purple',
    '#4B0082': 'Indigo',
    '#8A2BE2': 'Blue Violet',
    '#9932CC': 'Dark Orchid',
    '#9400D3': 'Dark Violet',
    '#BA55D3': 'Medium Orchid',
    '#DA70D6': 'Orchid',
    '#EE82EE': 'Violet',
    '#DDA0DD': 'Plum',
    '#D8BFD8': 'Thistle',
    '#FFFFFF': 'White',
    '#F5F5F5': 'White Smoke',
    '#DCDCDC': 'Gainsboro',
    '#D3D3D3': 'Light Grey',
    '#C0C0C0': 'Silver',
    '#A9A9A9': 'Dark Grey',
    '#808080': 'Grey',
    '#696969': 'Dim Grey',
    '#778899': 'Light Slate Grey',
    '#708090': 'Slate Grey',
    '#2F4F4F': 'Dark Slate Grey',
    '#000000': 'Black',
    '#A52A2A': 'Brown',
    '#8B4513': 'Saddle Brown',
    '#D2691E': 'Chocolate',
    '#CD853F': 'Peru',
    '#F4A460': 'Sandy Brown',
    '#DEB887': 'Burlywood',
    '#D2B48C': 'Tan',
    '#BC8F8F': 'Rosy Brown',
    '#FFE4C4': 'Bisque',
    '#FFEBCD': 'Blanched Almond',
    '#F5DEB3': 'Wheat',
    '#FF1493': 'Deep Pink',
    '#FF69B4': 'Hot Pink',
    '#FFB6C1': 'Light Pink',
    '#FFC0CB': 'Pink',
    '#DB7093': 'Pale Violet Red'
};

    function initTheme() {
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark' || (savedTheme === null && prefersDarkScheme)) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }
    themeToggle.addEventListener('click', function () {
        if (document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    });
    initTheme();
    imageInput.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (file && file.type.match('image.*')) {
            const reader = new FileReader();
            reader.onload = function (e) {
                previewImg.src = e.target.result;
                previewImg.classList.remove('hidden');
                placeholderContent.classList.add('hidden');
                previewImg.onload = function () {
                    extractColors(previewImg);
                };
            };
            reader.readAsDataURL(file);
        }
    });
    colorFormat.addEventListener('change', function () {
        updateColorCircles();
    });
    function extractColors(image) {
        try {
            extractedColors = colorThief.getPalette(image, 5);
            updateColorCircles();
        } catch (error) {
            console.error('Erro ao extrair cores:', error);
            alert('Não foi possível extrair cores desta imagem. Tente uma imagem diferente.');
        }
    }
    function findColorName(rgb) {
        const [r, g, b] = rgb;
        const hex = `#${componentToHex(r)}${componentToHex(g)}${componentToHex(b)}`;
        function colorDistance(hex1, hex2) {
            const r1 = parseInt(hex1.substring(1, 3), 16);
            const g1 = parseInt(hex1.substring(3, 5), 16);
            const b1 = parseInt(hex1.substring(5, 7), 16);
            const r2 = parseInt(hex2.substring(1, 3), 16);
            const g2 = parseInt(hex2.substring(3, 5), 16);
            const b2 = parseInt(hex2.substring(5, 7), 16);
            return Math.sqrt(Math.pow(r1 - r2, 2) + Math.pow(g1 - g2, 2) + Math.pow(b1 - b2, 2));
        }
        let closestColor = null;
        let minDistance = Infinity;
        for (const [knownHex, colorName] of Object.entries(colorNames)) {
            const distance = colorDistance(hex, knownHex);
            if (distance < minDistance) {
                minDistance = distance;
                closestColor = colorName;
            }
        }
        return minDistance < 50 ? closestColor : null;
    }
    function updateColorCircles() {
        colorsContainer.innerHTML = '';
        extractedColors.forEach(function (color) {
            const colorCode = formatColor(color);
            const colorCircle = document.createElement('div');
            colorCircle.className = 'color-circle';
            colorCircle.style.backgroundColor = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
            const colorName = findColorName(color);
            const colorLabel = document.createElement('div');
            colorLabel.className = 'text-center mt-2 text-sm font-mono';
            colorLabel.textContent = colorCode;
            const nameLabel = document.createElement('div');
            nameLabel.className = 'color-name text-center text-gray-600 dark:text-gray-400';
            nameLabel.textContent = colorName || '';
            const colorContainer = document.createElement('div');
            colorContainer.className = 'flex flex-col items-center';
            colorContainer.appendChild(colorCircle);
            colorContainer.appendChild(colorLabel);
            colorContainer.appendChild(nameLabel);
            colorCircle.addEventListener('click', function () {
                copyToClipboard(colorCode);
            });
            colorsContainer.appendChild(colorContainer);
        });
    }
    function formatColor(color) {
        const [r, g, b] = color;
        switch (colorFormat.value) {
            case 'hex':
                return `#${componentToHex(r)}${componentToHex(g)}${componentToHex(b)}`;
            case 'rgb':
                return `rgb(${r}, ${g}, ${b})`;
            case 'hsl':
                const [h, s, l] = rgbToHsl(r, g, b);
                return `hsl(${Math.round(h)}°, ${Math.round(s)}%, ${Math.round(l)}%)`;
            case 'cmyk':
                const [c, m, y, k] = rgbToCmyk(r, g, b);
                return `cmyk(${Math.round(c)}%, ${Math.round(m)}%, ${Math.round(y)}%, ${Math.round(k)}%)`;
            default:
                return `rgb(${r}, ${g}, ${b})`;
        }
    }
    function componentToHex(c) {
        const hex = c.toString(16);
        return hex.length === 1 ? '0' + hex : hex;
    }
    function rgbToHsl(r, g, b) {
        r /= 255;
        g /= 255;
        b /= 255;
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;
        if (max === min) {
            h = s = 0;
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                case g: h = (b - r) / d + 2; break;
                case b: h = (r - g) / d + 4; break;
            }
            h /= 6;
        }
        return [h * 360, s * 100, l * 100];
    }
    function rgbToCmyk(r, g, b) {
        r /= 255;
        g /= 255;
        b /= 255;
        const k = 1 - Math.max(r, g, b);
        const c = (1 - r - k) / (1 - k) || 0;
        const m = (1 - g - k) / (1 - k) || 0;
        const y = (1 - b - k) / (1 - k) || 0;
        return [c * 100, m * 100, y * 100, k * 100];
    }
    function copyToClipboard(text) {
        const tempInput = document.createElement('input');
        tempInput.value = text;
        document.body.appendChild(tempInput);
        tempInput.select();
        let success = false;
        try {
            success = document.execCommand('copy');
            if (!success) {
                navigator.clipboard.writeText(text)
                    .then(() => showNotification())
                    .catch(err => {
                        console.error('Both clipboard methods failed:', err);
                        showFallbackNotification(text);
                    });
            } else {
                showNotification();
            }
        } catch (err) {
            console.error('Error copying text:', err);
            showFallbackNotification(text);
        } finally {
            document.body.removeChild(tempInput);
        }
    }
    function showFallbackNotification(text) {
        notification.textContent = `Não foi possível copiar automaticamente. Use: ${text}`;
        notification.style.display = 'block';
        setTimeout(() => {
            notification.style.display = 'none';
            notification.textContent = 'Cor copiada para a área de transferência!';
        }, 3000);
    }
    function showNotification() {
        notification.style.display = 'block';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 2000);
    }
    imagePreview.addEventListener('dragover', function (e) {
        e.preventDefault();
        imagePreview.classList.add('border-blue-500');
    });
    imagePreview.addEventListener('dragleave', function () {
        imagePreview.classList.remove('border-blue-500');
    });
    imagePreview.addEventListener('drop', function (e) {
        e.preventDefault();
        imagePreview.classList.remove('border-blue-500');
        const file = e.dataTransfer.files[0];
        if (file && file.type.match('image.*')) {
            imageInput.files = e.dataTransfer.files;
            const event = new Event('change');
            imageInput.dispatchEvent(event);
        }
    });
    imagePreview.addEventListener('click', function () {
        imageInput.click();
    });
});