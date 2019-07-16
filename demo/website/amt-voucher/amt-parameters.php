
<?php
/*
 * Return AMT query string parameters.
 *
 */

$workerId = $_GET[workerId];
$assignmentId = $_GET[assignmentId];
$hitId = $_GET[hitId];
$turkSubmitTo = $_GET[turkSubmitTo];

// If AMT query string parameters don't exist, set to empty strings.
if (is_null($assignmentId)) {
    $workerId = "";
    $assignmentId = "";
    $hitId = "";
    $turkSubmitTo = "";
}

// Check if redirect came from live AMT site.
$isLive = 0;
if ($turkSubmitTo == "https://www.mturk.com") {
    $isLive = 1;
}

$info = array(
    "workerId"=>$workerId,
    "assignmentId"=>$assignmentId,
    "hitId"=>$hitId,
    "turkSubmitTo"=>$turkSubmitTo,
    "isLive"=>$isLive
);
echo json_encode($info);
?>