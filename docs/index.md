# NASOdyssey

![Image of NASOdyssey](main.jpg)

## Introduction

This page and repository documents my design and build of a small NAS server inspired by (but not a fork of) [this project](https://github.com/mattlokes/onash2).
This NAS is a gift for a relative with modest needs, but I've expanded on Matt's project in a number of ways:

* A different main board since the ODroid H2 is no longer available
* 3 drives rather than 2 for use with a ZFS setup
* A color OLED display running over SPI for faster, more colorful status screens

The NAS runs [OpenMediaVault](https://www.openmediavault.org/) and [Docker](https://www.docker.com/) and provides file sharing and basic app server functionality
for my parents.

## Index

* [Parts](#Parts)
* [Case](#Case)
  * [3D Printing](#3D-Printing)
  * [Hardware](#Hardware)
  * [Electronics](#Electronics)
    * [Arduino](#Arduino)
    * [OLED](#OLED)
* [Software](#Software)
  * [ArduinoFan](#ArduinoFan)
  * [Sysmon](#Sysmon)

## Parts

This is a fairly complete parts list, excluding the 3D printed parts and nuts and bolts which are detailed further down. Some substituions are possible.

| Item | Quantity | Notes |
| ---- | -------- | ----- |
| [Odyssey X86J4125864](https://www.seeedstudio.com/ODYSSEY-X86J4125864-p-4916.html) | 1 | Includes 64GB eMMC and 8GB RAM |
| [3.5" SATA drive](https://smile.amazon.com/gp/product/B08VH891FS/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1) | 3 | I used 2TB drives but you can go larger |
| [SATA power/data cable](https://www.seeedstudio.com/SATA-26AWG-200mm-p-4680.html) | 3 | |
| [SATA Expander](https://smile.amazon.com/gp/product/B07XYSK3QG/ref=ppx_yo_dt_b_asin_title_o06_s00?ie=UTF8&psc=1) | 1 | Adds 2 more SATA ports to the 1 already on the main board |
| [120mm 5V PWM fan](https://smile.amazon.com/gp/product/B07DXQTCK6/ref=ppx_yo_dt_b_asin_title_o05_s00?ie=UTF8&psc=1) | 1 | Needs to be a 5V fan! |
| [OLED display](https://smile.amazon.com/gp/product/B07DBXMFSN/ref=ppx_yo_dt_b_asin_title_o08_s00?ie=UTF8&psc=1) | 1 | This is a 1.5" RGB SPI display |
| [USB 3 extension](https://smile.amazon.com/gp/product/B08FLB9Q1N/ref=ppx_yo_dt_b_asin_title_o04_s00?ie=UTF8&psc=1) | 1 | I only used the "right" handed extension |
| [12V power supply](https://smile.amazon.com/gp/product/B00Z9X4GLW/ref=ppx_yo_dt_b_asin_title_o06_s00?ie=UTF8&psc=1) | 1 | This is a 10A supply which is a little overkill, but you need enough juice to get 3 HDD spinning |

## Case


### 3D Printing

### Hardware

### Electronics

#### Arduino

#### OLED

## Software

### ArduinoFan

### Sysmon
