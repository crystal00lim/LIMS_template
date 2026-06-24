document.addEventListener('DOMContentLoaded', function() {
    const script = document.getElementById('data');
    const data = JSON.parse(script.textContent);
    
    const doxy = data.doxy_series;
    const nodoxy = data.nodoxy_series;
    const x_labels = data.x_labels;
    const doxy_total = data.doxy_total;
    const nodoxy_total = data.nodoxy_total;

    console.log(doxy_total);

    const options = {
        chart: {
            type: 'line',
            height: 350,
            zoom: { enabled: false },
            group: 'participants',
            id: 'syncingChart',
            sync: {
                enabled: true
            }
        },
        xaxis: {
            categories: x_labels,
            title: {
                text: 'Visit Number',
                style: {
                    color: '#373D3F',
                    fontSize: '12px',
                }
            }
        },
        yaxis: {
            title: {
                text: '% of Positive Isolates',
                style: {
                    color: '#373D3F',
                    fontSize: '12px',
                }
            }
        }
    };

    var oneCharts = new ApexCharts(
        document.querySelector("#doxy"), {
            ...options,
            chart: {
                ...options.chart,
                id: 'doxyChart'
            },
            series: doxy,
            title: {
                text: 'Doxycycline',
                align: 'left'
            },
            tooltip: {
                shared: true,
                intersect: false,
                x: {
                    show: true,
                    formatter: function(value, { dataPointIndex }) {
                        const total = doxy_total[dataPointIndex];
                        return 'Visit ' + value + ' - ' + '<strong>' + total + ' participants</strong>';
                    }
                }
            }
        }
    );
    oneCharts.render();

    var secCharts = new ApexCharts(
        document.querySelector("#nondoxy"), {
            ...options,
            chart: {
                ...options.chart,
                id: 'nodoxyChart'
            },
            series: nodoxy,
            title: {
                text: 'Control',
                align: 'left'
            },
            tooltip: {
                shared: true,
                intersect: false,
                x: {
                    show: true,
                    formatter: function(value, { dataPointIndex }) {
                        const total = nodoxy_total[dataPointIndex];
                        return 'Visit ' + value + ' - ' + '<strong>' + total + ' participants</strong>';
                    }
                }
            }
        }
    );
    secCharts.render();
})