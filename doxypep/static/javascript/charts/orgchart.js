document.addEventListener('DOMContentLoaded', function() {
    const script = document.getElementById('orgs');
    console.log(script);
    const data = JSON.parse(script.textContent);

    const series = data.series;
    const labels = data.label;
    const title = data.title;


    var pieChart = new ApexCharts(
        document.querySelector("#orgChart"), {
            chart: {
                type: 'pie',
                toolbar: {
                    show: true
                },
                height: 350
            },
            title: {text: title, align: 'center'},
            series: series,
            labels: labels,
            fill: {
                colors: ['#D68100', '#00AC6B', '#0092FF', '#D6006B', '#7D00D6', '#D6D600', '#00D6CB']
            },
            responsive: [{
                breakpoint: 480
            }],
            
        }
    );
    pieChart.render();
})