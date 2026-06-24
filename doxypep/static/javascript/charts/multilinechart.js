document.addEventListener('DOMContentLoaded', function() {
    const series = JSON.parse(document.getElementById('multi_series').textContent);
    const labels = JSON.parse(document.getElementById('multi_labels').textContent);

    var multiChart = new ApexCharts(
        document.querySelector('#multiChart'), {
            chart: {
                type: 'line',
                height: 350,
                zoom: { enabled: false }
            },
            series: series,
            dataLabels: {
                enabled: false
            },
            stroke: {
                curve: 'straight',
                width: 3,
                dashArray: 0
            },
            title: {
                text: 'Positive Isolates Over Visit Number',
                align: 'left'
            },
            legend: {
                tooltipHoverFormatter: function(val, opts) {
                    const value = opts.w.globals.series[opts.seriesIndex][opts.dataPointIndex];
                    return val + ' - ' + '<strong>' + value + '%</strong>';
                }
            },
            markers: {
                size: 0,
                hover: {
                    sizeOffset: 6
                }
            },
            xaxis: {
                type: 'category',
                categories: labels,
            },
            tooltip: {
                shared: true,
                intersect: false,
            },
            grid: {
                borderColor: '#f1f1f1',
            }
        },
    );


    multiChart.render();
})