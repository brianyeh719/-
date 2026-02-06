from playwright.sync_api import sync_playwright

class THSRBot:
    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright = None

    def start_browser(self):
        self.playwright = sync_playwright().start()
        # Add stealth arguments
        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.page = self.browser.new_page()
        
        # Mask navigator.webdriver
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page.goto("https://irs.thsrc.com.tw/IMINT/")
        try:
            self.page.click("#cookieAccpetBtn", timeout=2000)
        except:
            pass # Cookie button might not be there

    def fill_form(self, start_station, dest_station, date, time_str, quantity, captcha_callback):
        # Start Station
        print(f"Debug: Selecting Start Station '{start_station}'...")
        try:
            self.page.select_option("#BookingS1Form_selectStartStation", label=start_station)
        except Exception as e:
            print(f"Error selecting Start Station: {e}")
        
        # Dest Station 
        print(f"Debug: Selecting Dest Station '{dest_station}'...")
        try:
            self.page.select_option("#BookingS1Form_selectDestinationStation", label=dest_station)
        except Exception as e:
            print(f"Error selecting Dest Station: {e}")
        
        # Date
        print(f"Debug: Setting Date to '{date}'...")
        try:
            # Use JS to set the hidden input directly, bypassing the read-only visible one
            # and handling the format mismatch (Hidden needs YYYY/MM/DD)
            self.page.evaluate(f"""() => {{
                const hiddenInput = document.getElementById('toTimeInputField');
                hiddenInput.value = '{date}'; 
                hiddenInput.dispatchEvent(new Event('change'));
            }}""")
            
            # Optional: Update visible input just for visual confirmation (if found)
            # The visible input is usually the next sibling
            self.page.evaluate(f"""() => {{
                const visibleInput = document.querySelector('#toTimeInputField').nextElementSibling;
                if (visibleInput) {{
                    visibleInput.value = '{date}'; 
                }}
            }}""")
            
            print("Debug: Date set via JS execution on hidden field.")
        except Exception as e:
            print(f"Error setting Date: {e}")

        # Time
        print(f"Debug: Selecting Time '{time_str}'...")
        try:
            self.page.select_option("select[name='toTimeTable']", label=time_str)
        except Exception as e:
            print(f"Error selecting Time: {e}")

        # Ticket Amount (Adult)
        print(f"Debug: Selecting Quantity '{quantity}'...")
        try:
            self.page.select_option("select[name='ticketPanel:rows:0:ticketAmount']", label=quantity)
        except Exception as e:
            print(f"Error selecting Quantity: {e}")

        # CAPTCHA
        print("Looking for CAPTCHA image...")
        captcha_selector = "#BookingS1Form_homeCaptcha_passCode"
        try:
            # Wait explicitly for the element to appear in DOM
            captcha_elem = self.page.wait_for_selector(captcha_selector, timeout=10000)
            
            # Wait for image to be loaded (naturalWidth > 0)
            self.page.wait_for_function(
                f"document.querySelector('{captcha_selector}').naturalWidth > 0",
                timeout=5000
            )

            print("Capturing CAPTCHA screenshot...")
            img_bytes = captcha_elem.screenshot()
            print(f"Screenshot taken, size: {len(img_bytes)} bytes")
            
            code = captcha_callback(img_bytes)
            print(f"User entered code: {code}")
            
            if code:
                self.page.fill("#securityCode", code)
            else:
                print("No code entered by user.")
        
        except Exception as e:
            print(f"Error finding/capturing CAPTCHA: {e}")
                
    def submit_search(self, start_station, dest_station, date, time_str, quantity, captcha_callback, stop_event=None):
        max_retries = 1000
        
        for i in range(max_retries):
            # Stop Check
            if stop_event and stop_event.is_set():
                print(">> Stop requested. Aborting search.")
                return False
            
            # Refill Form (to persist data across page resets)
            print(f"Refilling form (Attempt {i+1})...")
            self.fill_form(start_station, dest_station, date, time_str, quantity, captcha_callback)
            
            # Debug: Check CAPTCHA value
            code_val = self.page.input_value("#securityCode")
            print(f"Current Security Code value: '{code_val}'")
            
            # Click Submit
            print(f"Submitting search (Attempt {i+1})...")
            
            try:
                self.page.click("#SubmitButton", force=True)
            except Exception as e:
                print(f"Click exception: {e}")

            # Wait for reaction (page reload or navigation)
            # Increase timeout to allow for slower connections
            try:
                self.page.wait_for_load_state('networkidle', timeout=10000)
            except:
                self.page.wait_for_timeout(5000)
            
            # Check Stop Event again after wait
            if stop_event and stop_event.is_set():
                print(">> Stop requested. Aborting search.")
                return False

            # Detection Method 1: Check URL for S2
            current_url = self.page.url
            print(f"Current URL after submit: {current_url}")
            if "BookingS2Form" in current_url or "BookingS2" in current_url:
                print("URL indicates Step 2. Moving to train selection...")
                return True
            
            # Detection Method 2: Check for Step 2 DOM elements
            # The train result listing only exists on Step 2
            try:
                result_listing = self.page.query_selector(".result-listing")
                if result_listing and result_listing.is_visible():
                    print("Found .result-listing element! Successfully on Step 2.")
                    return True
            except:
                pass

                
            # Check for Errors (DOM based)
            # Note: The error element may exist but be hidden (display: none)
            try:
                error_elem = self.page.query_selector(".feedbackPanelERROR, #divErrMSG:not([style*='display: none']) .uk-alert-danger, #feedMSG span.error")
                
                # Also check if the error container is actually visible
                is_visible = False
                if error_elem:
                    try:
                        is_visible = error_elem.is_visible()
                    except:
                        # Fallback: check if parent is visible
                        pass
                
                if error_elem and is_visible:
                    error_text = error_elem.inner_text().strip()
                    
                    # Skip empty error messages
                    if not error_text or error_text == "error" or len(error_text) < 5:
                        print("Error element visible but empty, likely false positive.")
                    else:
                        print(f"Error found: {error_text}")
                        
                        # Case 1: Captcha Error -> Retry Immediately
                        if "檢測碼" in error_text or "Security Code" in error_text:
                            print(">> Captcha error detected. Retrying...")
                            continue 
                        
                        # Case 2: No Tickets / Sold Out -> Wait and Retry
                        if "查無" in error_text or "售完" in error_text or "No tickets" in error_text:
                            print(">> No tickets / Sold out. Waiting 5 seconds before retry...")
                            self.page.wait_for_timeout(5000)
                            continue
                else:
                    # No visible error element - check URL again
                    current_url = self.page.url
                    print(f"No visible error. Current URL: {current_url}")
                    if "BookingS2" in current_url or "S2Form" in current_url:
                        print("Successfully navigated to Step 2!")
                        return True

            except Exception as e:
                print(f"Error checking for messages: {e}")

            print(f"Retry {i+1}...")
            self.page.wait_for_timeout(2000)



    def submit_booking(self, person_id, phone, email=None, time_ranges=None, test_mode=True):
        print(f"Starting booking process... (Time Ranges: {time_ranges})")
        print(f"Test Mode: {'ON (will NOT submit)' if test_mode else 'OFF (will SUBMIT!)'}")

        try:
            # Step 2: Select Train
            # Wait for the result listing
            try:
                self.page.wait_for_selector(".result-listing", timeout=10000)
            except:
                print("Warning: .result-listing not found immediately.")

            target_radio = None
            target_dept_time = None
            
            # Get all radio inputs directly - they contain QueryDeparture as an attribute
            # Structure: <input QueryDeparture="06:34" QueryArrival="06:47" ... type="radio">
            radios = self.page.query_selector_all("input[name='TrainQueryDataViewPanel:TrainGroup']")
            print(f"Found {len(radios)} train radio buttons to scan.")
            
            # First, collect and log all available train departure times
            all_dept_times = []
            for radio in radios:
                dept_time = radio.get_attribute("QueryDeparture") or radio.get_attribute("querydeparture")
                if dept_time:
                    all_dept_times.append(dept_time.strip())
            print(f"Available train departure times: {all_dept_times}")
            print(f"User's priority time ranges: {time_ranges}")
            
            candidate_trains = [] # List of (priority, departure_time, radio_element)

            for radio in radios:
                # Extract Departure Time from the attribute (more reliable than span text)
                dept_time = radio.get_attribute("QueryDeparture")
                if not dept_time:
                    # Fallback: try lowercase (HTML is case-insensitive)
                    dept_time = radio.get_attribute("querydeparture")
                
                if not dept_time:
                    print("Warning: Could not extract QueryDeparture from radio, skipping.")
                    continue
                
                dept_time = dept_time.strip()
                
                # If no specific ranges, pick first available (Default behavior matching "Leave empty = earliest")
                if not time_ranges:
                    target_radio = radio
                    target_dept_time = dept_time
                    print(f"No specific range, selecting first available: {dept_time}")
                    break
                
                # Check priority against time ranges
                # time_ranges is list of tuples: [("09:00", "10:00"), ("14:00", "15:00")]
                # Lower index = Higher priority
                matched_priority = -1
                for idx, (start, end) in enumerate(time_ranges):
                    # String comparison works for HH:MM format
                    is_match = start <= dept_time <= end
                    print(f"  Checking {dept_time}: {start} <= {dept_time} <= {end} ? {is_match}")
                    if is_match:
                        matched_priority = idx
                        break
                
                if matched_priority != -1:
                    candidate_trains.append((matched_priority, dept_time, radio))
                    print(f">>> MATCH! {dept_time} matches Priority {matched_priority}")

            print(f"Total candidates found: {len(candidate_trains)}")
            
            if time_ranges:
                if candidate_trains:
                    # Sort by Priority (asc), then Time (asc)
                    candidate_trains.sort(key=lambda x: (x[0], x[1]))
                    best_match = candidate_trains[0]
                    print(f">> Selecting Best Match: {best_match[1]} (Priority {best_match[0]})")
                    target_radio = best_match[2]
                    target_dept_time = best_match[1]
                else:
                    print("=" * 50)
                    print("⚠️ 沒有符合優先時段的班次！")
                    print(">> 返回 Step 1 重新搜尋...")
                    print("=" * 50)
                    
                    # Click "回首頁" or the search again button to return to Step 1
                    # Look for the back/search again link
                    try:
                        # Try clicking the "查詢其他車次" or navigation back
                        back_link = self.page.query_selector("a.btn-reselectTrain, a[href*='BookingS1'], .btn-back, a:has-text('查詢更多車次')")
                        if back_link:
                            back_link.click()
                            self.page.wait_for_timeout(2000)
                        else:
                            # Navigate directly to home page
                            self.page.goto("https://irs.thsrc.com.tw/IMINT/")
                            self.page.wait_for_load_state("domcontentloaded")
                    except Exception as e:
                        print(f"Error navigating back: {e}")
                        # Fallback: just go to homepage
                        self.page.goto("https://irs.thsrc.com.tw/IMINT/")
                        self.page.wait_for_load_state("domcontentloaded")
                    
                    return "RETRY"  # Signal to caller to retry search


            if target_radio:
                # Scroll into view
                target_radio.scroll_into_view_if_needed()
                
                # Click the radio input directly
                # This triggers the site's JS: DynamicPanels.radioOnClick(this) and adds 'active' class
                print(f"Clicking radio for train departing at {target_dept_time}...")
                target_radio.click()
                self.page.wait_for_timeout(500)
                
                # Verify the parent label has 'active' class
                parent_label = target_radio.evaluate("el => el.closest('label.result-item')")
                if parent_label:
                    print("Radio clicked, parent label should now be active.")
                else:
                    print("Could not verify parent label, but proceeding.")

            else:
                print("No selectable train found!")
                return

            # Click Submit/Confirm for Step 2
            # Value is "確認車次", name="SubmitButton"
            print("Submitting Step 2 (Train Selection)...")
            self.page.click("input[name='SubmitButton']")
            
            # Wait for navigation to Step 3
            print("Waiting for Step 3 page to load...")
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            
            # Check for session error page (抱歉，無法繼續提供您訂票的服務)
            page_content = self.page.content()
            if "無法繼續提供您訂票的服務" in page_content or "抱歉" in page_content:
                print("ERROR: Session expired or invalid state detected!")
                print("The THSR system requires quick actions. Please restart the booking process.")
                return
            
            # Step 3: Passenger Info
            print("Entering passenger info (Step 3)...")
            
            # Wait for ID field (updated selector based on Step 3 HTML)
            # Input Name: "dummyId", ID: "idNumber"
            self.page.wait_for_selector("#idNumber", timeout=10000)

            
            # Fill ID
            print(f"Filling ID: {person_id}")
            self.page.fill("#idNumber", person_id)
            
            # Fill Phone
            # Input Name: "dummyPhone", ID: "mobilePhone"
            print(f"Filling Phone: {phone}")
            self.page.fill("#mobilePhone", phone)
            
            # Agree to Ticket Rules (Checkbox)
            # Name: "agree"
            print("Checking Agreement...")
            self.page.check("input[name='agree']") 
            
            # Fill Email (optional)
            if email:
                print(f"Filling Email: {email}")
                self.page.fill("#email", email)
            else:
                print("Email not provided, skipping.")
            
            print("Info filled. Ready to complete booking.")
            
            # Final Submit Button
            # ID: "isSubmit", Value: "完成訂位" (type="button")
            if test_mode:
                print("=" * 50)
                print("🧪 測試模式：已停止於最終確認頁面")
                print("   所有資料已填寫完成，但未送出訂位")
                print("   如需實際訂位，請取消勾選「測試模式」")
                print("=" * 50)
            else:
                print("=" * 50)
                print("🔴 正式模式：正在送出訂位...")
                print("=" * 50)
                # Click the final submit button
                self.page.click("#isSubmit")
                
                # Wait for response
                self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                
                # Check for success (Step 4 or confirmation)
                page_content = self.page.content()
                if "訂位成功" in page_content or "完成訂位" in page_content or "訂位代號" in page_content:
                    print("✅ 訂位成功！")
                    # Try to extract booking code
                    # This may vary based on actual Step 4 HTML
                    print("請查看瀏覽器確認訂位結果。")
                else:
                    print("訂位結果未知，請查看瀏覽器確認。")
                    self.page.screenshot(path="booking_result.png")
                    print("Screenshot saved to booking_result.png")
            
        except Exception as e:
            print(f"Error during booking: {e}")

            import traceback
            traceback.print_exc()
            self.page.screenshot(path="booking_error.png")
            print("Screenshot saved to booking_error.png")
        
    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
