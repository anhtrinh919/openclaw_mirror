# OpenClaw Tests Needed

A managed list of tests to perform for OpenClaw functionality. Reference and update this file as needed.

## Tests:

1. **Gmail Access/Test** [DONE]  
   - Verified: Authentication works; successfully searched and listed emails from yesterday. Ready for replies if needed.

2. **Calendar Access/Test** [DONE]  
   - Verified: Successfully listed events for tomorrow (Feb 26, 2026). Access works; one meeting found: "[MEETING] Xây dựng lại quy trình duyệt thông tin KM/ BQMS trên Base [LCM]" from 9:30-10:30 AM (Vietnam time).

3. **Daily Schedule Cron Job Test** [DONE]  
   - Verified: Successfully set up and added a one-shot cron job for the 8:30 AM reminder. Cron is running reliably for scheduled tasks.

4. **Google Sheets Management Stability Test** [DONE]  
   - Verified: Successfully created a new sheet "OpenClaw Tests Needed" (ID: 13VR9w-DNAdzUAqw_P2vkjb-EpuShGiwNsyLoHpM7zw4), added headers, appended all test rows data, and confirmed stability over multiple read/write operations.

5. **Node File Access and Command Run Test** [DONE]  
   - Verified: Successfully ran commands on Macbook Air node to create a text file ~/Downloads/openclaw_test.txt with 'Hello from OpenClaw!' message and read it back intact. Node access and execution are stable.