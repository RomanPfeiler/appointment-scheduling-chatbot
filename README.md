---
title: Appointment Scheduler
emoji: 🏦
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Appointment Scheduler

A conversational chatbot for booking bank appointments (Investing, Mortgage, Pension consultations).

Built with **Chainlit** + **Google Gemini API** as part of a CAS NLP project at the University of Bern.

This hosted demo runs the **Gemini-only** stack with **Smart availability search on by
default** (when a requested time is fully booked it offers nearby alternatives). The local
NLP model (Arm 2) is disabled on the hosted demo — it needs CPU inference that the free
Space hardware can't run — and the public demo caps each session at 50 messages.
