
# humtemp

## TODOs

 - Algorithm: Measure three times, go to sleep
 - Algorithm: When enough samples are measured, send to carbon
 - Handle getaddinfo OSError 2, temporary namespace resolution
 - Check deepsleep accuracy
 - Reuse time from last time after deepsleep
 - Redo ntp after TBD amount of time
 - Determine how much entries could be stored max
 - Determine how much entries to store
 - On transmission error, keep recording till somewhere close to max and retry

## Improvement Ideas

 - Do not even build output strings if debug is off
 - Use are more robust storage format than json, maybe line based with some sansity checks. In case of a broken file only affected entries should be lost.