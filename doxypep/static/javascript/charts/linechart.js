document.addEventListener('DOMContentLoaded', function() {
    const script = document.getElementById('data');
    // console.log(script);
    const data = JSON.parse(script.textContent);

    const labels = data.visit;
    const title = data.title;
    const seriesdata = data.series;

    const series = [
        {
            name: 'Control',
            data: seriesdata.control
        },
        {
            name: 'Experimental',
            data: seriesdata.experimental
        },
        {
            name: 'Partner',
            data: seriesdata.partner
        }
    ];

    var multiChart = new ApexCharts(
        document.querySelector('#lineChart'), {
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
                width: 3
            },
            title: {
                text: title,
                align: 'left'
            },
            xaxis: {
                type: 'category',
                categories: labels,
                title : {
                    text: 'Visit Number'
                }
            },
            yaxis: {
                title: {
                    text: '% of Resistant Participants'
                }
            },
            tooltip: {
                shared: true,
                intersect: false,
            },
            grid: {
                borderColor: '#f1f1f1',
            }
        }
    );

    multiChart.render();
});