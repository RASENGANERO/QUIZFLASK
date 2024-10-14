function getInputData() {
    dt = [];
    let s=document.getElementsByTagName('input');
    for(let i=0;i<s.length;i++){
        if(s[i].hasAttribute('quiz-text')==true){
           dt.push(String(s[i].value)); 
        }
    }
    return dt.join("\n");
}
$(document).ready(function() {
    $("#quiz-form").on("submit", function (event) {
        event.preventDefault();
        let number =document.getElementById("submitform").getAttribute("number-list"); 
        data = {
            listid: number,
            data: getInputData()
        };
        $.ajax({
            url:"/skillanswer/"+String(number)+"/",
            type: 'POST',
            data: JSON.stringify(data),
            contentType: "application/json",
            success: function(response) {
                let dt = response;
                if (dt["isfinal"]=="true") {
                    window.location.href="/skillreport/";
                }
                window.location.href="/skill/"+dt["next"]+"/";
                
            }
        });
    });
});




