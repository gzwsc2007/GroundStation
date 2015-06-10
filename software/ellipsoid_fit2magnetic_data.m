function [ Bfield, offset, W_inverted ] = ellipsoid_fit2magnetic_data(M)
%
% Fit an ellispoid to a set of xyz data points
%compansate hard-iron, soft-iron and scaling effects.


% Parameters:
% M   - Cartesian data, n x 3 matrix (Containing magnetic data mx,my,mz as columns)

% Output:
% Bfield    -  Radius of sphere having same volume with elipsoid fitted to data 
% offset    -  ellispoid center coordinates [xc; yc; zc](used for Hard-iron effect compansation)
%W_inverted -  Matrix needed to transform data (vector) on the elipsoidal
%surface  to a spherical surface (used for Soft-Iron effect and scaling/calibration error compansation)

%Definitions
% * radii     -  ellipsoid radii [a; b; c]
% * evecs     -  ellipsoid radii directions as columns of the 3x3 matrix
% * v         -  the 9 parameters describing the ellipsoid algebraically: 
%                Ax^2 + By^2 + Cz^2 + 2Dxy + 2Exz + 2Fyz + 2Gx + 2Hy + 2Iz = 1

% Author:
% Ozan AKTA?
% Turkey, Ankara
%

 x = M( :, 1 );
 y = M( :, 2 );
 z = M( :, 3 );
    
 D = [ x .* x, ...
       y .* y, ...
       z .* z, ...
      2 * x .* y, ...
      2 * x .* z, ...
      2 * y .* z, ...
      2 * x, ...
      2 * y, ... 
      2 * z ];  % n data points x 9 ellipsoid parameters
  

% solve the normal system of equations and find fitted ellipsoid parameters
v = ( D' * D ) \ ( D' * ones( size( x, 1 ), 1 ) );

% form the algebraic form of the ellipsoid
    A = [ v(1) v(4) v(5) v(7); ...
          v(4) v(2) v(6) v(8); ...
          v(5) v(6) v(3) v(9); ...
          v(7) v(8) v(9) -1 ];
    % find the center of the ellipsoid
    offset = A( 1:3, 1:3 ) \ [ v(7); v(8); v(9) ];
 
    
 %remove offset, do same calculation again written in a simplified algebraic form of elipsoid   
 x = x+offset(1);
 y = y+offset(2);
 z = z+offset(3);
  
 K = [ x .* x, ...
       y .* y, ...
       z .* z, ...
      2 * x .* y, ...
      2 * x .* z, ...
      2 * y .* z];  %
    
    % solve the normal system of equations
    p = ( K' * K ) \ ( K' * ones( size( x, 1 ), 1 ) );
    
    % form the algebraic form of the ellipsoid with center at (0,0,0)
    AA = [ p(1) p(4) p(5) ; ...
          p(4)  p(2) p(6) ; ...
          p(5)  p(6) p(3) ];
      
    % solve the eigenproblem
    [ evecs evals ] = eig( AA );
    radii = sqrt( 1 ./ diag( evals ) );
    
    %calculate radius of sphere having same volume with the elipsoid 
    Bfield=(radii(1)*radii(2)*radii(3))^(1/3);
    
    %calculate transformation matrix elipsoidal to spherical
    W_inverted=evecs*sqrt(evals)*inv(evecs)*Bfield;
    
    correctedM=W_inverted*[x';y';z'];
    
% draw raw data and corrected data
figure;
hold on;
grid on;

%plot corrected data with offset and eccentricity removed
plot3( correctedM(1,:),correctedM(2,:) , correctedM(3,:),'r' );

%Plot raw data with offset removed (for visual purposes).
plot3( x, y, z ); 

%draw elipsoidal fit to raw data with offset removed
maxd = max( [ radii(1) radii(2) radii(3)] );

step = maxd / 50;
[ xx, yy, zz ] = meshgrid( -maxd:step:maxd, -maxd:step:maxd, -maxd:step:maxd  );

Ellipsoid = p(1) *xx.*xx +   p(2) * yy.*yy + p(3) * zz.*zz + ...
          2*p(4) *xx.*yy + 2*p(5)*xx.*zz + 2*p(6) * yy.*zz ;

isosurface( xx, yy, zz, Ellipsoid, 1 );
alpha(.4);
axis square
view([-45 45]);