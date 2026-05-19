# Pinky Rig — Production-Ready Biped Roadmap

Target: feature-complete human biped by end of summer 2026
Branch: feature/production-ready-biped

## Decisions (locked)

- Mirror strategy: A path (positive scale + axis flip)
- Maya version floor: 2022
- offsetParentMatrix: yes (2020+)
- blendMatrix node: yes (2022+)
- aimMatrix node: yes (2022+)
- Constraint replacement: hybrid — matrix for spaceswitch / follow / offset stacking,
  pm.constraint stays for driver-driven jnt and IK/FK blend

## Milestones

### M1 — Global scale ✓ DONE
- [✓] root_ctrl scale propagates to all components
- [✓] joint_grp inherits scale
- [✓] Test: scale root_ctrl 2x, full biped scales uniformly
- Estimated: 1-2 days

### M2 — Matrix constraint module
- [ ] core/matrix_constraint.py skeleton
- [ ] matrix_parent helper (offsetParentMatrix based)
- [ ] matrix_blend helper (blendMatrix based)
- [ ] matrix_aim helper (aimMatrix based)
- [ ] tests/manual/test_matrix_constraint.py — minimal scene tests
  - [ ] Test offset preservation
  - [ ] Test scale propagation
  - [ ] Test mirror compatibility (A path)
  - [ ] Test save/reopen file
- Estimated: 1-2 weeks

### M3 — Spaceswitch / follow system
- [ ] Settings ctrl exposes follow attribute (enum: world / parent / chest / etc)
- [ ] ArmRig: arm follow chest / world
- [ ] NeckRig: head follow chest / world / global
- [ ] LegRig: leg follow root / world
- [ ] Switch with no pop (offset preserved)
- [ ] Test on biped: switch during animation, verify no jump
- Estimated: 2-3 weeks

### M4 — IK stretch + elbow/knee lock + volume
- [ ] ArmRig: IK stretch with measure
- [ ] LegRig: IK stretch
- [ ] Elbow / knee lock (pin to PV)
- [ ] Volume preservation on stretch
- Estimated: 1-2 weeks

### M5 — Production polish
- [ ] Rotation order exposed on all FK ctrls
- [ ] Ctrl visibility toggle on settings ctrl (FK / IK / detail layers)
- [ ] Color convention enforced (L red, R blue, M yellow)
- [ ] Ctrl shape consistent (IK box, FK circle, global arrow)
- Estimated: 1 week

### M6 — Bendy / ribbon (stretch goal)
- [ ] ArmRig: bendy upper / lower
- [ ] LegRig: bendy upper / lower
- [ ] Twist distribution (use existing quaternion twist work)
- Estimated: 2 weeks (drop if running out of time)

## Deferred (not this summer)

- Facial component
- New creature components (quadruped, wings)
- _update_rotation refactor (waiting for more components to find right abstraction)
- Pure math IK option (existing IFK limb work, integrate later)
- UE Control Rig demo

## Hard stop

- August 31, 2026: whatever state framework is in becomes v1.0
- Sep 1, 2026: focus shift to Japanese (繁田塾 + self-study)
- Demo character work pushed to autumn
