document.addEventListener('DOMContentLoaded', function() {
    const script = document.getElementById('rdata');

    const data = JSON.parse(script.textContent);

    const series = data.data;

    const title = data.title;

    var radialbar = new ApexCharts(
        document.querySelector('#radialbar'), {
            series: series,
            chart: {
                type: 'radialBar',
                sparkline: {
                    enabled: true
                }
            },
            plotOptions: {
                radialBar: {
                    startAngle: -90,
                    endAngle: 90,
                },
                dataLabels:{
                    name: {
                        show: false
                    },
                    value: {
                        offsetY: -2
                    }
                }   
            },
            labels: false,
        },
    );

    radialbar.render();
});