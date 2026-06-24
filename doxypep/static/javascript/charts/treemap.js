document.addEventListener('DOMContentLoaded', function() {
    const script = document.getElementById('treetrust');
    const data = JSON.parse(script.textContent);
    const series = data.series;
    const title = data.title;

    const formattedSeries = [{
        name: data.title || 'Sequence Types', 
        data: data.series                    
    }];

    const yValues = formattedSeries[0].data.map(item => item.y);
    const highestValue = Math.max(...yValues);

    // ✨ FIX 1: Calculate the total sum of all 'y' values for the percentage calculation
    const totalSum = yValues.reduce((sum, value) => sum + value, 0);

    var treemap = new ApexCharts(
        document.querySelector("#treemap"), {
            series: formattedSeries,
            chart: {
                type: 'treemap',
                height: 350
            },
            title: { text: title, align: 'center' },
            legend: {
                show: true,
                offsetY: 10, // ✨ FIX 2: Corrected 'iffsetY' typo to 'offsetY'
                height: 30,
            },
            plotOptions: {
                treemap: {
                //    enableShades: true,
                //    shadeTo: 'dark',
                //    colorScale: {
                //        ranges: [{
                //            from: 0,
                //            to: highestValue,
                //            color: '#228848'
                //        }]
                //    }
                },
            },
            dataLabels: {
                enabled: true,
                formatter: function(text, op) {
                    // const value = op.value;
                    // if (!totalSum) return [text, '0%'];
                    // const percentage = ((value / totalSum) * 100).toFixed(1);
                    return text;
                }
            },
            tooltip: {
                enabled: true,
                y: {
                    formatter: function(value) {
                        if (!totalSum) return '0%';
                        const percentage = ((value / totalSum) * 100).toFixed(1);
                        
                        // Option A: Just show the percentage
                        return percentage + '%';
                        
                    }
                },
            },
            responsive: [{
                breakpoint: 480
            }],
        }
    );
    treemap.render();
});