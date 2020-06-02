#!/usr/bin/env bash
png2sp1sprite ./sprite_sample.png -m ./sprite_sample_mask.png -i circle_masked > circle_sprite_masked.asm
zcc +zx -vn -m -startup=31 -clib=sdcc_iy circle_masked.c circle_sprite_masked.asm -o circle_masked -create-app
