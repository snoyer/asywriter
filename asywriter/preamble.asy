import geometry;
import palette;

path   make_cyclic(path   p){ return cyclic(p) ? p : p--cycle; }
guide  make_cyclic(guide  g){ return cyclic(g) ? g : g--cycle; }
path[] make_cyclic(path[] ps){
    path[] qs = new path[ps.length];
    for(int i = 0; i < ps.length; ++i)
        qs[i] = make_cyclic(ps[i]);
    return qs;
}
