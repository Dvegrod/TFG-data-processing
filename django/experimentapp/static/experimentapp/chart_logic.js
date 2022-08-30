
const down = (ctx, value) => ctx.p0.parsed.y < ctx.p1.parsed.y ? value : undefined;

const genericOptions = {
    fill: false,
    interaction: {
        intersect: false
    },
    animation: {
        onComplete: () => {
            delayed = true;
        },
        delay: (context) => {
            let delay = 0;
            if (context.type === 'data' && context.mode === 'default' && !delayed) {
                delay = context.dataIndex * 300 + context.datasetIndex * 100;
            }
            return delay;
        },
    },
    radius: 0,
};

chart_properties = {
    borderColor: 'rgb(75, 192, 192)',
    segment: {
        borderColor: ctx => down(ctx, 'rgb(192,75,75)'),
    },
    spanGaps: true
};


function configure_chart(id, url) {
    select = $("#" + id);
    chart_info = $.ajax({
        type: "GET",
        url : url,
        data: {},
        async: false
    });
    chart_data = JSON.parse(chart_info.responseText);
    new Chart(
        select,
        {
            type: chart_data.type,
            data: {
                labels : chart_data.data.labels,
                datasets : [{
                    label : chart_data.data.datasets[0].label,
                    data : chart_data.data.datasets[0].data,
                    borderColor: chart_properties.borderColor,
                    segment: chart_properties.segment,
                    spanGaps: chart_properties.spanGaps
                }],
            },
            options: genericOptions
        }
    );
}

function update_charts() {
    
}
