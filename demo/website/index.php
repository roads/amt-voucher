<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset='utf-8'>
    <title>Voucher Demo</title>

    <!-- jQuery library -->
    <script src="https://code.jquery.com/jquery-3.3.1.js" integrity="sha256-2Kok7MbOyxpgUVvAk/HJ2jigOSYS2auK4Pfzbm7uH60=" crossorigin="anonymous"></script>
    <!-- Bootstap - Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">

    <!-- The voucher stylesheet must be included in the header. -->
    <link rel='stylesheet' href='amt-voucher/voucher-style.css'>
</head>

<body>

    <noscript>
        <h1>Warning: Javascript seems to be disabled</h1>
        <p>This website requires that Javascript be enabled on your browser.</p>
        <p>Instructions for enabling Javascript in your browser can be found <a href="http://support.google.com/bin/answer.py?hl=en&answer=23852">here</a></p>
    </noscript>

    <div class="container-fluid">
        <div class="row">
            <div class="col"></div>
            <div class="col-4">    
                <button id=complete-button>Complete Task</button>
                <br/>
                <br/>
            </div>
            <div class="col"></div>
        </div>

        <div class="row">
            <div class="col"></div>
            <div class="col-4">
                <?php require "amt-voucher/voucher.php"; ?>
            </div>
            <div class="col"></div>
        </div>
    </div>

    <script src="amt-voucher/voucher.js"></script>
    <script type="text/javascript">
        var appState = {};
        var amtParameters = <?php require "amt-voucher/amt-parameters.php"; ?>;
        var voucherCode = "";
    
        $(window).on('load', function(){
            appState = {
                workerId: amtParameters['workerId'],
                amtAssignmentId: amtParameters["assignmentId"],
                amtHitId: amtParameters["hitId"],
                amtSubmitTo: amtParameters["turkSubmitTo"],
                amtIsLive: amtParameters["isLive"],
                voucherCode: ""
            };
        });

        $('#complete-button').click( function() {
            Handle_Voucher(appState)            
        });

    </script>

</body>

</html>
