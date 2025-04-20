document.addEventListener('DOMContentLoaded', function() {
    const exportForm = document.getElementById('exportForm');
    
    exportForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(exportForm);
        const data = {
            dataRange: formData.get('dataRange'),
            format: formData.get('format'),
            includeScores: formData.get('includeScores') === 'on',
            includeTimestamps: formData.get('includeTimestamps') === 'on',
            includeContent: formData.get('includeContent') === 'on',
            includeWordCloud: false
        };

        console.log('Export data:', data);

        const submitButton = exportForm.querySelector('button[type="submit"]');
        submitButton.classList.add('loading');
        submitButton.disabled = true;

        try {
            if (data.format === 'copy') {
                await handleCopyToClipboard(data);
            } else if (data.format === 'png') {
                await handleImageExport(data);
            } else if (data.format === 'pdf' || data.format === 'csv') {
                await handleFileExport(data);
            } else {
                throw new Error('Unsupported export format');
            }
            showNotification(`Export successful!`, 'success');
        } catch (error) {
            console.error('Export error:', error);
            showNotification('Failed to export data. Please try again.', 'error');
        } finally {
            submitButton.classList.remove('loading');
            submitButton.disabled = false;
        }
    });

    // Format options visual feedback
    const formatOptions = document.querySelectorAll('.format-option');
    formatOptions.forEach(option => {
        const radio = option.querySelector('input[type="radio"]');
        radio.addEventListener('change', function() {
            formatOptions.forEach(opt => opt.classList.remove('active'));
            option.classList.add('active');
        });
        
        if (radio.checked) {
            option.classList.add('active');
        }
    });
});

async function handleCopyToClipboard(data) {
    console.log('Copying to clipboard...');
    const response = await fetch('/export/data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    if (!response.ok) {
        const errorText = await response.text();
        console.error('Server response:', errorText);
        throw new Error('Failed to fetch data');
    }
    
    const result = await response.json();
    console.log('Received data:', result);
    
    // Format the data for clipboard
    const formattedData = result.data.map(item => {
        let formatted = {};
        if (data.includeTimestamps) formatted.Date = item.created_at;
        if (data.includeScores) {
            formatted.Sentiment = item.sentiment;
            formatted.Confidence = `${item.confidence}%`;
        }
        if (data.includeContent) formatted.Content = item.text;
        return formatted;
    });

    const prettyData = JSON.stringify(formattedData, null, 2);
    await navigator.clipboard.writeText(prettyData);
}

async function handleImageExport(data) {
    console.log('Exporting image...');
    const response = await fetch('/export/data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    if (!response.ok) {
        const errorText = await response.text();
        console.error('Server response:', errorText);
        throw new Error('Failed to fetch data');
    }
    
    const result = await response.json();
    console.log('Received data:', result);
    
    // Create a temporary container
    const container = document.createElement('div');
    container.style.cssText = `
        padding: 40px;
        background: white;
        max-width: 1200px;
        margin: 0 auto;
        font-family: Arial, sans-serif;
    `;
    
    // Add content to container
    container.innerHTML = `
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #333; margin-bottom: 10px; font-size: 24px;">Sentiment Analysis Export</h1>
            <p style="color: #666; margin-bottom: 20px;">Export Date: ${new Date().toLocaleDateString()}</p>
            <p style="color: #666;">Data Range: ${data.dataRange === 'recent' ? 'Last 30 days' : 'All time'}</p>
        </div>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <thead>
                <tr style="background: #f8f9fa;">
                    ${data.includeTimestamps ? '<th style="padding: 12px 15px; text-align: left; border-bottom: 2px solid #ddd; color: #333;">Date</th>' : ''}
                    ${data.includeScores ? `
                        <th style="padding: 12px 15px; text-align: left; border-bottom: 2px solid #ddd; color: #333;">Sentiment</th>
                        <th style="padding: 12px 15px; text-align: left; border-bottom: 2px solid #ddd; color: #333;">Confidence</th>
                    ` : ''}
                    ${data.includeContent ? '<th style="padding: 12px 15px; text-align: left; border-bottom: 2px solid #ddd; color: #333;">Content</th>' : ''}
                </tr>
            </thead>
            <tbody>
                ${result.data.map((item, index) => `
                    <tr style="background: ${index % 2 === 0 ? '#ffffff' : '#f8f9fa'};">
                        ${data.includeTimestamps ? `
                            <td style="padding: 12px 15px; border-bottom: 1px solid #ddd; color: #666;">
                                ${item.created_at}
                            </td>
                        ` : ''}
                        ${data.includeScores ? `
                            <td style="padding: 12px 15px; border-bottom: 1px solid #ddd; color: #666;">
                                <span style="
                                    display: inline-block;
                                    padding: 4px 8px;
                                    border-radius: 4px;
                                    background: ${
                                        item.sentiment === 'positive' ? '#e3fcef' :
                                        item.sentiment === 'negative' ? '#ffe3e3' : '#f8f9fa'
                                    };
                                    color: ${
                                        item.sentiment === 'positive' ? '#0ca678' :
                                        item.sentiment === 'negative' ? '#e03131' : '#495057'
                                    };
                                ">
                                    ${item.sentiment}
                                </span>
                            </td>
                            <td style="padding: 12px 15px; border-bottom: 1px solid #ddd; color: #666;">
                                ${Math.round(item.confidence * 100)}%
                            </td>
                        ` : ''}
                        ${data.includeContent ? `
                            <td style="padding: 12px 15px; border-bottom: 1px solid #ddd; color: #666;">
                                ${item.text}
                            </td>
                        ` : ''}
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    document.body.appendChild(container);
    
    const canvas = await html2canvas(container, {
        scale: 2,
        logging: false,
        useCORS: true,
        backgroundColor: '#ffffff',
        windowWidth: 1200,
        width: 1200
    });
    
    document.body.removeChild(container);
    
    const imageUrl = canvas.toDataURL('image/png', 1.0);
    const downloadLink = document.createElement('a');
    downloadLink.href = imageUrl;
    downloadLink.download = 'sentiment-analysis-export.png';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

async function handleFileExport(data) {
    console.log('Exporting file...', data.format);
    const response = await fetch('/export/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': data.format === 'pdf' ? 'application/pdf' : 'text/csv'
        },
        body: JSON.stringify(data)
    });
    
    if (!response.ok) {
        const errorText = await response.text();
        console.error('Server response:', errorText);
        throw new Error('Failed to generate file');
    }
    
    const blob = await response.blob();
    console.log('Received blob:', blob.type, blob.size);
    
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sentiment-analysis-export.${data.format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => notification.classList.add('show'), 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

// Add notification styles
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        border-radius: 8px;
        background: var(--card-bg);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateX(120%);
        transition: transform 0.3s ease;
        z-index: 1000;
    }

    .notification.show {
        transform: translateX(0);
    }

    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--text-color);
    }

    .notification.success i {
        color: var(--dracula-green);
    }

    .notification.error i {
        color: var(--dracula-red);
    }
`;
document.head.appendChild(style); 