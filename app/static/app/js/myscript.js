$('#slider1, #slider2, #slider3').owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
        0: {
            items: 2,
            nav: false,
            autoplay: true,
        },
        600: {
            items: 4,
            nav: true,
            autoplay: true,
        },
        1000: {
            items: 6,
            nav: true,
            loop: true,
            autoplay: true,
        }
    }
})

$('.plus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this.parentNode.children[2]
    $.ajax({
        type:"GET",
        url:"/pluscart",
        data:{
            prod_id:id
        },
        success:function(data){
            eml.innerText=data.quantity
            document.getElementById("amount").innerText=data.amount
            document.getElementById("totalamount").innerText=data.totalamount
        }
    })
})

$('.minus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this.parentNode.children[2]
    $.ajax({
        type:"GET",
        url:"/minuscart",
        data:{
            prod_id:id
        },
        success:function(data){
            eml.innerText=data.quantity
            document.getElementById("amount").innerText=data.amount
            document.getElementById("totalamount").innerText=data.totalamount
        }
    })
})


$('.remove-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this
    $.ajax({
        type:"GET",
        url:"/removecart",
        data:{
            prod_id:id
        },
        success:function(data){
            document.getElementById("amount").innerText=data.amount
            document.getElementById("totalamount").innerText=data.totalamount
            eml.parentNode.parentNode.parentNode.parentNode.remove()
        }
    })
})


$('.plus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/pluswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            //alert(data.message)
            window.location.href = `http://localhost:8000/product-detail/${id}`
        }
    })
})


$('.minus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/minuswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            window.location.href = `http://localhost:8000/product-detail/${id}`
        }
    })
})



console.log("myscript.js LOADED");

window.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".mo-ta").forEach(function(moTa){

        const btn = moTa.parentElement.querySelector(".xem-them");
        if(!btn) return;

        // nếu chiều cao thật = chiều cao hiển thị -> text không bị cắt
        if(moTa.scrollHeight <= moTa.clientHeight + 1){
            btn.style.display = "none";
        }

    });

});

window.toggleMoTa = function(btn){

    const moTa = btn.parentElement.querySelector(".mo-ta");

    if(moTa.classList.contains("text-collapse")){
        moTa.classList.remove("text-collapse");
        btn.innerText = "Thu gọn";
    }else{
        moTa.classList.add("text-collapse");
        btn.innerText = "Xem thêm";
    }

};

document.addEventListener("DOMContentLoaded", function () {

    const monthData = JSON.parse(document.getElementById("monthData").textContent || "[]");
    const revenueData = JSON.parse(document.getElementById("revenueData").textContent || "[]");

    // ===== CHART THÁNG =====
    if (monthData.length) {
        window.chartMonth = new Chart(document.getElementById('chartMonth'), {
            type: 'bar',
            data: {
                labels: monthData.map(i => i.month ? i.month.substring(0,7) : ''),
                datasets: [{
                    label: 'Lượt đặt',
                    data: monthData.map(i => i.count)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // ===== CHART DOANH THU =====
    if (revenueData.length) {
        window.chartRevenue = new Chart(document.getElementById('chartRevenue'), {
            type: 'pie',
            data: {
                labels: revenueData.map(i => i.ma_tour__ma_dia_diem__ten_dia_diem),
                datasets: [{
                    data: revenueData.map(i => i.revenue || 0)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

});


// ===== EXPORT PDF =====
function exportPDF() {

    const img1 = document.getElementById("chartMonth").toDataURL("image/png");
    const img2 = document.getElementById("chartRevenue").toDataURL("image/png");

    const form = document.createElement("form");
    form.method = "POST";
    form.action = "";   // ❗ bỏ ?export=pdf

    const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;

    form.innerHTML = `
        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf}">
        <input type="hidden" name="export" value="pdf">   <!-- QUAN TRỌNG -->
        <input type="hidden" name="chart_month" value="${img1}">
        <input type="hidden" name="chart_revenue" value="${img2}">
    `;

    document.body.appendChild(form);
    form.submit();
}