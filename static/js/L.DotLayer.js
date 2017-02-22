/* Canvas Layer */
let DOT_CONSTS = {
  1: [10000, 1],
  2: [5000, 1],
  3: [3000, 1],
  4: [2000, 1],
  5: [1000, 1],
  6: [900, 1],
  7: [800, 2],
  8: [700, 2],
  9: [600, 2],
  10: [500, 3],
  11: [400, 3],
  12: [300, 4],
  13: [200, 4],
  14: [100, 5],
  15: [50, 5],
  16: [50, 5],
  17: [30, 6],
  18: [15, 6],
  19: [15, 7],
  20: [10, 7]
};

function drawDots(info, A, time) {
    if (!info.bounds.intersects(A.bounds)) {
        return 0;
    }

    const times = A.time,
          latlngs = A.latlng,
          max_time = times[times.length-1],
          zoom = info.zoom,
          delay = DOT_CONSTS[zoom][0],
          num_pts = Math.floor(max_time / delay),
          ctx = info.canvas.getContext('2d');

    let s = time % max_time,
        key_time = s - delay * Math.floor(s/delay),
        count = 0,
        i = 0,
        t, d, dt, p1, p2, p, size, interval_good;

    if (A.highlighted) {
        size = 4;
        ctx.fillStyle = "#FFFFFF";
    } else {
        size = 2;
        ctx.fillStyle = "#000000";
    }

    for (let j = 0; j < num_pts; j++) {
        t = (key_time + j*delay);
        if (t >= times[i]) {
          while (t >= times[i]) {
            i++;
          }

          p1 = latlngs[i-1];
          p2 = latlngs[i];
          interval_good = info.bounds.contains(p1) || info.bounds.contains(p2);

          if (interval_good) {
              dt = times[i] - times[i-1];
              M = [(p2[0]-p1[0])/dt,  (p2[1]-p1[1])/dt];
          }
        }

        if (interval_good) {

            dt = t - times[i-1];
            p = [p1[0] + M[0]*dt, p1[1] + M[1]*dt];

            if (info.bounds.contains(p)) {
                dot = info.layer._map.latLngToContainerPoint(p);
                // ctx.fillRect(dot.x-1, dot.y-1, size, size);
                ctx.beginPath();
                ctx.arc(dot.x, dot.y, size, 0, Math.PI * 2);
                ctx.fill();
                ctx.closePath();
                count++;
            }
        }

    }

    return delay;

}

/* for dot paths */
function onDrawLayer(info) {
    let now = Date.now();

    let ctx = info.canvas.getContext('2d'),
        zoom = info.zoom,
        time = (now - this.start_time) >>> DOT_CONSTS[zoom][1],
        delay = 0;

    ctx.clearRect(0, 0, info.canvas.width, info.canvas.height);
    let ids = Object.keys(appState.items);
    for (i = 0; i < ids.length; i++) {
        let A = appState.items[ids[i]];
        if (("time" in A) && ("latlng" in A)) {
            delay = drawDots(info, A, time);
        } else {
            console.log(A);
        }
    }

    fps_display.update(now, " delay=" + delay + " zoom="+info.zoom);

}

function animate() {
  this.paused = false;
  this.start_time = Date.now();
  L.Util.requestAnimFrame(this._animate, this);
}

function pause() {
  this.paused = true;
}

function _animate() {
    if (!this.paused) {
      this.drawLayer();
      L.Util.requestAnimFrame(this._animate, this);
    }
}