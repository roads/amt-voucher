function Handle_Voucher(appState) {
    // Uncomment the if/else statement if you only want voucher codes to be
    // generated for AMT workers.
    // if (appState.amtAssignmentId != "") {
        $(".voucher__present").show();
        if (appState.voucherCode == "") {
            var dataToPost = {
                amtIsLive: appState.amtIsLive,
                amtAssignmentId: appState.amtAssignmentId,
                amtWorkerId: appState.workerId,
                amtHitId: appState.amtHitId,
            };
            // Create new voucher entry in database.
            $.post("amt-voucher/post-voucher.php", dataToPost, function(voucherStatus) {
                console.log("voucher status: " + voucherStatus);
                if (voucherStatus != "0") {
                    appState.voucherCode = voucherStatus;
                    $(".voucher__code").text(appState.voucherCode);
                }
            }).fail( function (xhr, status, error) {
                console.log("Post using post-voucher.php failed.");
                console.log(status);
                console.log(error);
                console.log(xhr.responseText);
            }); // end post
        } else {
            $(".voucher__code").text(appState.voucherCode);
        }
    // } else {
    //     $(".voucher__absent").show();
    // }
}

$(".voucher__box").click( function() {
    $(".voucher__code").focus();
    $(".voucher__code").select();
});