# FRONTEND BOOTSTRAP AND BACKEND CONNECTION

## 1. Purpose

This document defines the first real frontend bootstrap for `docs-agent` operator application and its first backend connection wave.

## 2. Scope

Included:
- Vite + React frontend bootstrap
- operator shell layout
- backend task API integration
- task list/details/history loading
- task creation
- task state updates

Excluded:
- real Drive runtime
- real authority registry loading
- real package review runtime
- auth/session layer
- persistence beyond mock backend

## 3. Goal

The goal is to create the first live local operator app loop:
- frontend shell
- backend task API
- task state
- history

## 4. Final interpretation

This step replaces missing frontend runtime with a real application shell connected to the backend.
