// PicoConsole Pebble Mini v0.2, original design, GPL-3.0-or-later.
// Millimetres. Assembly: X right, Y up, Z from rear toward player.
// See README.md before printing. Prototype; vertical hardware dimensions
// and the control centres need a physical fit check.

part = "assembly"; // front, rear, retainer, cap, joystick, coupon, assembly
board = "pico2"; // pico2 or marble
key = 0; // 0=A, 1=B, 2=X, 3=Y, matching the physical LCD board
socket = 2.10;
header_gap = 11.0; // main PCB component-side plane to LCD PCB underside
button_tip = 2.30; // plunger bottom above LCD PCB; adjust after dry fit
sd_side = 1; // +1 is right; -1 permits a flipped Marble mounting
$fn = 64;
eps = 0.02;

wall = 2.0;
floor_thickness = 1.6;
// Keep 1.6 mm beneath a 1.6 mm main PCB. Header gap determines the height.
lcd_top = floor_thickness + 1.6 + 1.6 + header_gap + 1.6;
seam = lcd_top-2.0;
lcd_thickness = 1.6;
face_inner = lcd_top+4.0;
face_top = face_inner+1.4;
button_face = face_top+.7;
retainer_z = lcd_top+1.6;
joystick_z = lcd_top+5.1;
button_x = 21.9;
joystick_x = -19.3;
button_pitch = 5.7;
keys = ["A", "B", "X", "Y"];
function key_y(i) = (1.5-i)*button_pitch;
function main_top() = lcd_top-lcd_thickness-header_gap;
function clamp_points() = [for(x=[-24.3,24.3],y=[-12.3,12.3]) [x,y]];
// Top/bottom positions keep screw shafts out of the USB plug and SD card paths.
function screw_points() = [for(x=[-19.0,19.0],y=[-13.7,13.7]) [x,y]];

module rounded2(w,h,r=1) {
    offset(r=r) square([w-2*r,h-2*r],center=true);
}
module pebble2(inset=0) {
    offset(delta=-inset) rounded2(64,34,6);
}
module envelope(z0,z1,inset0=0,inset1=0) {
    hull() {
        translate([0,0,z0]) linear_extrude(eps) pebble2(inset0);
        translate([0,0,z1-eps]) linear_extrude(eps) pebble2(inset1);
    }
}
module slot2(w,h,r=1) { rounded2(w,h,r); }
module through_slot(x,y,w,h,z0,z1,r=1) {
    translate([x,y,z0]) linear_extrude(z1-z0) slot2(w,h,r);
}
module corner_pressers(z0,z1) {
    for(p=clamp_points()) translate([p[0],p[1],z0])
        cylinder(r=.80,h=z1-z0);
}
module screw_bosses(z0,z1) {
    for(p=screw_points()) translate([p[0],p[1],z0]) cylinder(d=4.2,h=z1-z0);
}
module grip_grooves() {
    for(side=[-1,1], y=[-8,-4,0,4,8])
        translate([side*29.0,y,face_top-.25])
        linear_extrude(.4) rounded2(1.4,.65,.3);
}
module front_shell() {
    difference() {
        union() {
            difference() {
                union() {
                    envelope(seam,face_top-1.2,0,0);
                    envelope(face_top-1.2,face_top,0,1.2);
                }
                translate([0,0,seam-.1]) linear_extrude(face_inner-seam+.1)
                    pebble2(wall);
            }
            screw_bosses(lcd_top+.25,face_inner+.1);
            corner_pressers(lcd_top+.15,face_inner+.1);
            // The retainer is captured by the closed shell, with no extra screws.
            for(y=[-12.3,12.3]) translate([27.5,y,retainer_z+1.15])
                cylinder(r=.8,h=face_inner-retainer_z-1.05);
        }
        // Small clearance around the full active image, not an oversized glass hole.
        through_slot(0,0,24.7,24.7,face_inner-.1,face_top+.2,1.1);
        through_slot(joystick_x,0,8.0,8.0,lcd_top-1,face_top+.2,3.9);
        for(i=[0:3]) through_slot(button_x,key_y(i),10.0,5.15,lcd_top+2.8,button_face+.5,.95);
        for(p=screw_points()) translate([p[0],p[1],lcd_top+.15])
            cylinder(d=1.65,h=face_inner-lcd_top+.05);
        // Open inner rabbet: 0.25 mm clearance around the 0.8 mm rear lip.
        translate([0,0,seam-.1]) linear_extrude(1.7)
            difference() { pebble2(.90); pebble2(2.10); }
        grip_grooves();
    }
}
module port_wells() {
    // USB is only about 6 mm behind the new end wall; keep a cable-boot corridor.
    translate([-36,-8.5,3.0]) cube([13,17,7.8]);
    if(board=="marble") {
        // J12 TF-018 opens at the opposite end to USB. Includes finger access.
        translate([sd_side*31,1.17,6.0]) cube([18,15.5,6.0],center=true);
        translate([sd_side*31,1.17,6.0]) rotate([0,90,0]) cylinder(d=8,h=12,center=true);
    }
}
module rear_shell() {
    difference() {
        union() {
            difference() {
                union() {
                    envelope(0,1.0,1.0,0);
                    envelope(1.0,seam,0,0);
                }
                translate([0,0,floor_thickness]) linear_extrude(seam+2) pebble2(wall);
            }
            screw_bosses(0,seam);
            // Four PCB-edge shelves: no load on the LCD glass or electronics.
            for(p=clamp_points()) translate([p[0],p[1],floor_thickness-.1])
                cylinder(r=.80,h=lcd_top-lcd_thickness-floor_thickness+.1);
            // LCD edge locators outside the PCB, joined to the shelves by ribs.
            for(side=[-1,1],y=[-12.3,12.3]) {
                translate([side*27.3,y,floor_thickness-.1]) cylinder(d=1.8,h=lcd_top-floor_thickness+.1);
                hull() for(x=[side*24.3,side*27.3])
                    translate([x,y,floor_thickness-.1]) cylinder(r=.8,h=lcd_top-lcd_thickness-floor_thickness+.1);
            }
            for(y=[-12.3,12.3]) {
                translate([27.5,y,floor_thickness-.1]) cylinder(r=.8,h=retainer_z-floor_thickness+.1);
                translate([27.5,y,retainer_z-.01]) cylinder(d=1.0,h=1.06);
            }
            translate([0,0,seam-.1]) linear_extrude(1.5)
                difference() { pebble2(1.15); pebble2(1.95); }
        }
        for(p=screw_points()) {
            translate([p[0],p[1],-.1]) cylinder(d=2.25,h=lcd_top+1);
            translate([p[0],p[1],-.1]) cylinder(d=3.9,h=1.0);
        }
        port_wells();
        // Back service access. PCB locations are nominal; verify before probing.
        if(board=="pico2") translate([-11.3,-3.5,-.1]) cylinder(d=5.0,h=floor_thickness+.2);
        else for(p=[[-6.317,6.039],[9.429,5.901]])
            translate([p[0],p[1],-.1]) cylinder(d=5.0,h=floor_thickness+.2);
        translate([0,-4,.35]) rotate([180,0,0]) linear_extrude(.38)
            text(board=="marble"?"MARBLE / SD":"PICO 2",size=3,font="Liberation Sans:style=Bold",halign="center",valign="center");
    }
}
module retainer() {
    difference() {
        translate([23.1,0,retainer_z]) linear_extrude(1.0) rounded2(10.6,26.2,1.2);
        for(i=[0:3]) through_slot(button_x,key_y(i),5.3,4.35,retainer_z-.1,retainer_z+1.2,.5);
        for(y=[-12.3,12.3]) {
            translate([24.3,y,retainer_z-.1]) cylinder(d=2.2,h=1.3);
            translate([27.5,y,retainer_z-.1]) cylinder(d=1.6,h=1.3);
        }
        for(p=screw_points()) translate([p[0],p[1],retainer_z-.1]) cylinder(d=4.8,h=1.3);
    }
}
module icon2(i) {
    if(i==0) polygon([[-1,-1.2],[-1,1.2],[1.1,0]]); // play
    if(i==1) union() { // list / change collection
        for(y=[-.9,0,.9]) translate([0,y]) rounded2(2.5,.48,.2);
    }
    if(i==2) polygon([for(j=[0:9]) let(a=90+j*36,r=j%2==0?1.5:.68) [r*cos(a),r*sin(a)]]);
    if(i==3) union() { // home / return to launcher
        polygon([[-1.4,0],[0,1.3],[1.4,0]]);
        difference() { translate([0,-.55]) square([2.0,1.3],center=true); translate([0,-.95]) square([.55,.7],center=true); }
    }
}
module cap_marks(i) {
    translate([-2.0,0]) text(keys[i],size=3.15,font="Liberation Sans:style=Bold",halign="center",valign="center");
    translate([2.1,0]) icon2(i);
}
module button_cap(i) {
    difference() {
        union() {
            translate([0,0,lcd_top+3.2]) linear_extrude(.7) rounded2(10.4,5.28,.9);
            translate([0,0,lcd_top+3.7]) linear_extrude(button_face-lcd_top-3.7) rounded2(9.4,4.65,.95);
            translate([0,0,lcd_top+button_tip]) cylinder(d=2.4,h=3.75-button_tip);
        }
        translate([0,0,button_face-.42]) linear_extrude(.6) cap_marks(i);
    }
}
module joystick_cap() {
    difference() {
        union() {
            cylinder(d=5,h=1.1);
            translate([0,0,1]) cylinder(d1=5,d2=12,h=3.5);
            translate([0,0,4.45]) cylinder(d=12,h=.55);
        }
        // No metal screw or excessive interference on the fragile joystick.
        translate([0,0,-.1]) linear_extrude(2.1) square([socket,socket],center=true);
        translate([0,0,19.1]) sphere(r=14.8);
        for(a=[0:90:270]) rotate([0,0,a]) translate([0,4.7,4.7])
            linear_extrude(.5) rounded2(.65,1.1,.3);
    }
}
module fit_coupon() {
    difference() {
        linear_extrude(2.2) rounded2(56.6,31.1,2);
        translate([0,0,-.1]) linear_extrude(2.4) rounded2(52.6,27.1,1.3);
    }
    translate([28,0,0]) cube([4,3,2.2]);
    difference() {
        translate([38,0,0]) linear_extrude(2.2) rounded2(14,31.1,2);
        for(i=[0:2]) translate([38,-8+i*8,-.1]) linear_extrude(2.4)
            square([2.00+i*.10,2.00+i*.10],center=true);
        for(i=[0:2]) translate([42,-8+i*8,1.8]) linear_extrude(.5)
            text(str(2.00+i*.10),size=1.6,halign="center",valign="center");
    }
}
module hardware_preview() {
    // Simplified keep-out envelopes, not manufacturer CAD.
    color([.05,.22,.19]) translate([0,0,lcd_top-.8]) cube([52,26.5,1.6],center=true);
    color([.03,.03,.04]) translate([1.8,0,lcd_top+1.8]) cube([29.5,26.5,3.6],center=true);
    color([.02,.03,.04]) translate([0,0,lcd_top+3.9]) cube([23.4,23.4,.15],center=true);
    color([.04,.32,.23]) translate([0,0,main_top()-.8]) cube([51,21,1.6],center=true);
}
if(part=="front") translate([0,0,face_top]) rotate([180,0,0]) front_shell();
else if(part=="rear") rear_shell();
else if(part=="retainer") translate([-23.1,0,-retainer_z]) retainer();
else if(part=="cap") translate([0,0,button_face]) rotate([180,0,0]) button_cap(key);
else if(part=="joystick") joystick_cap();
else if(part=="coupon") fit_coupon();
else if(part=="check-shells") intersection() {
    // Ignore the intended coincident seam plane with a 0.01 mm Z tolerance.
    front_shell(); translate([0,0,-.01]) rear_shell();
}
else if(part=="check-caps") intersection() {
    union() { front_shell(); retainer(); }
    union() for(i=[0:3]) translate([button_x,key_y(i),0]) button_cap(i);
}
else if(part=="check-retainer") intersection() {
    union() { front_shell(); rear_shell(); }
    // Exclude intended planar seating on the two locating posts.
    translate([0,0,.01]) retainer();
}
else if(part=="check-lcd") intersection() {
    union() { front_shell(); rear_shell(); retainer(); }
    // Shrink the nominal PCB by 0.02 mm to exclude intended seating contact.
    translate([0,0,lcd_top-.8]) cube([51.96,26.46,1.56],center=true);
}
else if(part=="check-hardware") intersection() {
    union() { front_shell(); rear_shell(); retainer(); }
    union() {
        translate([0,0,main_top()-.8]) cube([50.82,20.96,1.56],center=true);
        translate([1.8,0,lcd_top+1.8]) cube([29.46,26.46,3.56],center=true);
        translate([-24,0,main_top()+1.6]) cube([6.96,8.96,3.16],center=true);
        translate([20,1.17,main_top()+1]) cube([15.46,13.96,1.96],center=true);
    }
}
else if(part=="check-fastener-ports") intersection() {
    union() for(p=screw_points()) translate([p[0],p[1],0]) cylinder(d=2,h=face_top);
    port_wells();
}
else if(part=="assembly") {
    color([.10,.16,.26]) front_shell();
    color([.04,.48,.48]) rear_shell();
    color([.2,.2,.2]) retainer();
    for(i=[0:3]) color(i==0?[.45,.85,.4]:i==1?[1,.65,.25]:i==2?[.35,.7,1]:[.95,.45,.65])
        translate([button_x,key_y(i),0]) button_cap(i);
    color([1,.72,.20]) translate([joystick_x,0,joystick_z]) joystick_cap();
    hardware_preview();
}
