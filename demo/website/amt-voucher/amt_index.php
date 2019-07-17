<!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>Mechanical Turk Experiment</title>

        <script src="https://code.jquery.com/jquery-3.3.1.js" integrity="sha256-2Kok7MbOyxpgUVvAk/HJ2jigOSYS2auK4Pfzbm7uH60=" crossorigin="anonymous"></script>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
        
        <style type='text/css'>
            body {
                padding: 0;
                margin: 0;
                font-family: Georgia, serif;
                font-size: 1em;
                line-height: 1.25em;
            }

            p {
                margin-top: .625em;
                margin-bottom: .625em;
            }

            h1 {
                font-weight: bold;
                font-size: 1.25em;
                margin-top: .625em;
                margin-bottom: .625em;
            }

            ul {
                margin: 1em 0;
            }

            input[type=text] {
                font-size: 1.6em;
                font-family: Georgia, serif;
                /* border-radius: 5px; */
                padding: 10px;
                border: 3px solid #ccc;
                -webkit-transition: 0.5s;
                transition: 0.5s;
                outline: none;
            }

            input[type=text]:focus {
                border: 3px solid #555;
            }

            input[type='submit'] {
                font-size: 1.6em;
                font-family: Georgia, serif;
                /* border-radius: 5px; */
                /* margin: auto; */
                /* display: block; */
                padding: 10px;
                background-color: cornflowerblue;
            }

            input[type='submit']:hover {
                cursor: pointer;
            }

            .centered-heading {
                text-align: center;
            }

            div.scroll {
                width: auto;
                height: 310px;
                overflow: scroll;
                background-color: #e6e6e6;
            }

            .hide{
                display: none;
            }

            .submit-full{
                display: block;
            }
		</style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <div class="col"></div>
                <div class="col-10">
                    <div id="preview-content" class="hide">
                    <h2 class="centered-heading">Call for Participants</h2>

                    <p>Awesome Lab at Cool Research Institution is looking for online participants for an experiment studying how people do interesting things.</p>

                    <p><strong>Brief Description:</strong> You will be see stimuli and be asked to do something.</p>
                    
                    <p><strong>Duration:</strong> You will complete multiple trials, which typically takes some amount of time.</p>

                    <p><strong>Requirements:</strong></p>
                    <ul>
                        <li>You are at least 18 years old,</li>
                        <li>You have normal vision or wear corrective lenses, and</li>
                        <li>You are a fluent English speaker.</li>
                        <li>The experiment will only work in recent browsers, and may have issues loading on slower connections.</li>
                    </ul>
                    </div>
                </div>
                <div class="col"></div>
            </div>
            <div class="row">
                <div class="col"></div>
                <div class="col-10">
                    <div id="accept-content" class="hide row">
                        <p>By clicking the button below, you will be directed to an
                            external website that runs the experiment and provided with detailed instructions. At the end of the experiment, you will
                            receive a <strong>voucher code</strong>. Enter the voucher code below to complete the HIT.
                        </p>

                        <!-- Form to re-direct to external page. The action field must be modified to point to a real URL. -->
                        <form id="amt-redirect-form" method="GET" action="https://mywebsite.com/voucher-demo/index.php" target="_blank">
                            <input type="hidden" class="assignmentId" name="assignmentId" value="" />
                            <input type="hidden" class="workerId" name="workerId" value="" />
                            <input type="hidden" class="hitId" name="hitId" value="" />
                            <input type="hidden" class="isLive" name="isLive" value="" />
                            <input type="submit" class="submit-full" value="Go to experiment" />
                        </form>
                        
                        <br/>
                        <br/>
                        <br/>

                        <!-- Form to submit to AMT. -->
                        <form id="amt-submit-form" method="POST">
                            <input type="hidden" class="assignmentId" name="assignmentId" value="">
                            <input type="hidden" class="workerId" name="workerId" value="">
                            <input type="hidden" class="hitId" name="hitId" value="">
                            <div class="row">
                                <input type="text" class="col-9 voucher-code" name="voucherCode" placeholder="Enter voucher code here" autocomplete="off" required>
                                <input type="submit" class="col-3 voucher-submit" value="Submit" />
                            </div>
                        </form>
                    </div>
                </div>
                <div class="col"></div>
            </div>
        </div>
        <script type="text/javascript">
            // Query string function.
            function getParameterByName(name, url) {
                if (!url) url = window.location.href;
                name = name.replace(/[\[\]]/g, '\\$&');
                var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
                    results = regex.exec(url);
                if (!results) return null;
                if (!results[2]) return '';
                return decodeURIComponent(results[2].replace(/\+/g, ' '));
            }

            // $(window).load(function() {
            $(window).on('load', function(){
                var assignmentId = getParameterByName('assignmentId');
                var hitId = getParameterByName('hitId');
                var workerId = getParameterByName('workerId');
                var turkSubmitTo = getParameterByName('turkSubmitTo');
                var isLive = -1

                var submitUrl = ""
                if (turkSubmitTo === "https://workersandbox.mturk.com") {
                    submitUrl = "https://workersandbox.mturk.com/mturk/externalSubmit"
                    isLive = 0
                } else if (turkSubmitTo === "https://www.mturk.com") {
                    submitUrl = "https://www.mturk.com/mturk/externalSubmit"
                    isLive = 1
                }
                
                if (assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE') {
                    // Worker is viewing a preview (has not accepted HIT yet).
                    $("#preview-content").show();
                    $("#accept-content").hide();
                } else {
                    // Worker has accepted the HIT.
                    $("#preview-content").show();
                    $("#accept-content").show();

                    $(".assignmentId").val(assignmentId);
                    $(".hitId").val(hitId);
                    $(".workerId").val(workerId);
                    $(".isLive").val(isLive);

                    $("#amt-submit-form").attr('action', submitUrl);
                }
            });
        </script>
    </body>
</html>
