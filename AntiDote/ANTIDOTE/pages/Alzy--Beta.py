    # AI Chatbot
    with tab_ai:
        st.subheader("🤖 AI Chatbot")
        st.caption("Speak (mic) or type. Short, friendly answers.")

        # --- Conversation thread ---
        for msg in st.session_state.patient_ai_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # --- Previous questions list + Clear button ---
        st.markdown("**Previous questions**")
        c_q1, c_q2 = st.columns([3, 1])
        with c_q1:
            if st.session_state.patient_ai_questions:
                for i, q in enumerate(reversed(st.session_state.patient_ai_questions), 1):
                    st.write(f"{i}. {q}")
            else:
                st.caption("No previous questions yet.")
        with c_q2:
            if st.button("🗑️ Clear previous", key="clear_prev_q"):
                # reset questions + chat (keep friendly greeting)
                st.session_state.patient_ai_questions = []
                st.session_state.patient_ai_chat = [
                    {
                        "role": "assistant",
                        "content": "Hello 👋 I'm your Memory Assistant. How can I help you today?"
                    }
                ]
                st.success("Cleared all previous questions and chat history.")
                st.rerun()

        # --- Speech-to-text "Speak" button ---
        st.markdown(
            """
            <div style="margin:8px 0 12px 0;">
              <button id="stt-btn" style="padding:6px 14px;border:none;background:#f97316;color:white;border-radius:8px;cursor:pointer;">
                🎤 Speak
              </button>
              <span id="stt-status" style="margin-left:8px;font-size:12px;color:#fff;"></span>
            </div>
            <script>
            (function(){
              const btn    = document.getElementById("stt-btn");
              const status = document.getElementById("stt-status");
              if (!btn) return;

              btn.addEventListener("click", function(){
                status.textContent = "";
                const isLocal = (location.hostname === "localhost" || location.hostname === "127.0.0.1");
                if (!window.isSecureContext && !isLocal){
                  status.textContent = "❌ Mic blocked: use https or localhost.";
                  return;
                }
                const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SR){
                  status.textContent = "❌ SpeechRecognition not supported.";
                  return;
                }
                const rec = new SR();
                rec.lang = "en-US";

                rec.onstart = function(){
                  status.textContent = "Listening...";
                };
                rec.onerror = function(e){
                  status.textContent = "❌ " + (e.error || "Error");
                };
                rec.onend = function(){
                  if (status.textContent === "Listening...") {
                    status.textContent = "";
                  }
                };
                rec.onresult = function(e){
                  const text = e.results[0][0].transcript;
                  status.textContent = "Heard: " + text;
                  try {
                    // Use parent frame URL (like GPS code) so Streamlit sees the query param
                    const frameWin = window.parent || window;
                    const u = new URL(frameWin.location.href);
                    u.searchParams.set('say', text);
                    frameWin.location.href = u.toString();
                  } catch (err) {
                    console.error(err);
                    status.textContent = "❌ Could not send speech to app.";
                  }
                };
                rec.start();
              });
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )

        # --- Chat input (typed or spoken) ---
        spoken = get_qp("say")
        typed = st.chat_input("Type your message")
        user_input = spoken if spoken else typed

        last_reply = None

        if user_input:
            # store question in history
            st.session_state.patient_ai_questions.append(user_input)

            # Clear ?say= from URL after we used it (so it's not reused on refresh)
            if spoken:
                components.html(
                    """
                    <script>
                    (function(){
                      try {
                        const frameWin = window.parent || window;
                        const u = new URL(frameWin.location.href);
                        u.searchParams.delete('say');
                        frameWin.history.replaceState({}, '', u.toString());
                      } catch (e) {}
                    })();
                    </script>
                    """,
                    height=0,
                )

            # add user message to chat
            st.session_state.patient_ai_chat.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Local date/time override first
            reply_text = maybe_local_answer(user_input)
            api_key = OPENAI_API_KEY

            if reply_text is None:
                reply_text = f"I heard: {user_input}. I couldn't reach AI right now."

                if api_key:
                    try:
                        url = "https://api.openai.com/v1/chat/completions"
                        headers = {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        }
                        msgs = [
                            {
                                "role": "system",
                                "content": (
                                    "You are a gentle assistant for an Alzheimer's patient. "
                                    "Reply in 2–3 short, simple sentences. Be friendly. "
                                    "If the user asks for date or time, assume Indian time zone (IST)."
                                ),
                            }
                        ] + st.session_state.patient_ai_chat[-6:]
                        payload = {
                            "model": "gpt-4o-mini",
                            "messages": msgs,
                            "max_tokens": 150,
                            "temperature": 0.6,
                        }
                        resp = requests.post(url, headers=headers, json=payload, timeout=15)
                        if resp.status_code == 200:
                            j = resp.json()
                            reply_text = j.get("choices", [{}])[0].get("message", {}).get("content", "I’m here with you.")
                        else:
                            reply_text = f"⚠️ API error {resp.status_code}: {resp.text[:160]}"
                    except Exception as e:
                        reply_text = f"⚠️ Request failed: {e}"
                else:
                    reply_text = "❗ No OPENAI_API_KEY found.\nAdd it to your .env or Streamlit Secrets."

            # show assistant reply
            with st.chat_message("assistant"):
                st.markdown(reply_text)

            st.session_state.patient_ai_chat.append({"role": "assistant", "content": reply_text})
            last_reply = reply_text
        else:
            # no new input; take last assistant reply for TTS
            for m in reversed(st.session_state.patient_ai_chat):
                if m["role"] == "assistant":
                    last_reply = m["content"]
                    break

        # --- Read aloud last answer (TTS) ---
        if last_reply:
            safe_last_js = json.dumps(last_reply)
            components.html(
                """
                <button id="tts-btn" style="margin-top:10px;padding:6px 14px;border:none;background:#0ea5e9;color:white;border-radius:8px;cursor:pointer;">
                  🔊 Read aloud last answer
                </button>
                <script>
                (function(){
                  const btn = document.getElementById("tts-btn");
                  if(!btn) return;
                  const text = %s;
                  btn.addEventListener("click", function(){
                    if(!window.speechSynthesis){
                      alert("Speech not supported here.");
                      return;
                    }
                    try { window.speechSynthesis.cancel(); } catch(e) {}
                    const u = new SpeechSynthesisUtterance(text);
                    u.lang = "en-US";
                    u.rate = 0.95;
                    u.pitch = 1.0;
                    u.volume = 1.0;
                    window.speechSynthesis.speak(u);
                  });
                })();
                </script>
                """ % safe_last_js,
                height=70,
            )
