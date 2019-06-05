# RTNI_light
<p>
This is a light and user-friendly version of the program originally developped in the following paper: <br>
M. Fukuda, R. Koenig, I. Nechita "RTNI - A symbolic integrator for Haar-random tensor networks",<br> 
<a href="https://arxiv.org/abs/1902.08539">arXiv:1902.08539 [quant-ph]</a>
</p>
<p>  
On this website, one can average matrices symbolically with respect to Haar unitary at easy, but
there are limitations unlike the above original program:
<ul>
<li>All matrices are <img src="https://latex.codecogs.com/gif.latex?\inline&space;n \times n" />.</li> 
<li>Only two i.i.d. Haar unitary matrices are allowed.</li>
<li>The number of conjugate pairs of each Haar unitary matrix should not exceed two.</li>
</ul>
The second and third conditions are set to save computational resource of the server.  
One can download the program and customize them:<br>           
<a href="https://github.com/MotohisaFukuda/RTNI_light">RTNI_light at GitHub</a></p>
</p>
Also, one can get the Weingarten functions upto the size of twenty.

<hr>

<h3>Integration with respect to the Haar unitary.</h3>

<p>
An input is a sequence of two kinds of brackets and each bracket contains alphabets and some selected symbols (spaces will be ignored).
<ul>
<li> [ ] represents application of trace operation and ( ) otherwise.</li>
<li>Matrices are represented by upper and lower cases of alphabets at your choince, except for U and V, 
which are reserved for i.i.d. random Haar unitary matrices.</li>
<li>+,-,* are used to represent transpose, complex conjugate and adjoint, respectively.</li>
</ul>
Some examples (you do not need "" for the input.):
<ul>
<li>"Trace`[U^(**)AU] xx`Trace`[U^(+)BU^(-)]`" should be written as "[U*AU][U+BU-]".</li>
<li>"Trace`[U^(**)AU] UCU^(**)`" should be written as "[U*AU](UCU*)".</li>
<li>"`U^(**)AU^(T) ox UCDU^(**) ox VADV^(-)`" should be written as "(U*AU+)(UCDU*)(VADV-)".</li>
</ul>

Note that those top-right symbols in AsciiMath: `T`, `-` and `**` are used in the output format,
to represent transpose, complex conjugate and adjoint, respectively.
</p>

<hr>


<h3>Getting Weingarten functions.</h3>

<p>
An input is a set of numbers separated by commas. For example, 
<ul>
<li>"4,2,5" will give you the Weingarten function of the type (5,4,2).</li>
</ul>
where the input numbers are ordered automatically.
</p>

<hr>

<hr>
<h3>How to read the output data.</h3>
<p>
The bracket "( )" represents the space which was connected to the matrix in the bracket.
For example,
<ul>
<li>The average of "UAU*", which means `UAU^(**)`, is `frac{1}{n}[ `Trace`[  A^(T) ] xx (U)(U^(**))]`, which means `frac{1}{n}`Trace`[ A^(T) ] I`. <br>
Note that the identigy matrix exists implicitely between `(U)` and `(U^(**))`.
</li>
<li>The average of "(UAU-)", which meeans `UAU^(-)`, is `frac{1}{n}[(U) A^(T)(U^(-))]`, which means `frac{1}{n} A^(T)`. <br>
Here, the output could be written `frac{1}{n}[(U^(-)) A(U)]`, which is the same.
In this case, the output side of the matrix A is connected to the space which was originally connected to U^(-), which means that `A` is transposed.
</li>
<li>
The average of "(UV)(U-V-)". which means `UV ox U^(-)V^(-)`, is `frac{1}{1}[(U)(U^(-)) ox (V)(V^(-))]`. <br>
This is just unmormalized Bell state.
</li>
</ul>
</p>

<p>
In the pythonic data:
<ul>
<li>
The number, including `n`, is the weight.
</li>
<li>
In each pair (tuple object), the former is the tensor structure and the latter trace structure.
</li>
<li>
[1,1], [-1,1], [1,-1], [-1,-1] correspond respectively to no operation, transpose, complex conjugate and adjoint.
</li>
</ul>
</p>



















<img src="https://latex.codecogs.com/gif.latex?" />
<img src="https://latex.codecogs.com/gif.latex?\inline&space;F_s" />
