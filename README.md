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

Hosted Demo: https://huggingface.co/spaces/JosefPilter/appointments-chatbot

The hosted demo runs the **Gemini-only** stack with **Smart availability search on by
default** (when a requested time is fully booked it offers nearby alternatives). The local
NLP model is disabled on the hosted demo. The public demo caps each session at 50 messages.
