addpath('~/drivers/1');

trip = csvread([num2str(1) '.csv'], 1, 0);
trip = rotate(trip);
trip = trip(1:50,:);

% trip = [0 0 ; 0 2 ; 1 2; 1 4 ; 0 4 ; 1 1 ; 0 0 ; -10 -10 ; -5 -7 ; 0 -3.5 ] * -1;
% trip = [1:100 ; 1:2:200]';  
% trip = [trip ; [1.11:200 ; [-199:2:0] * -1]'];  
% trip = [1:100 ; 1:100]';  
% trip = [trip ; [101:200 ; [-100:-1] * -1]'];  

% trip = [repmat(1,1,100); 1:100 ]';
straight = zeros(size(trip,1),1);

threshold = pi/32; % between zero and 2*pi

data = [];

for iter = 2 : size(trip,1) - 1
    tmp = trip(iter-1,:) - trip(iter,:); 
    angle1 = atan2(tmp(2), tmp(1));
    tmp = trip(iter,:)  - trip(iter+1,:);
    angle2 = atan2(tmp(2), tmp(1));
%     data = [data ; abs(angle1 - angle2)];
    straight(iter) = abs(angle1 - angle2) <= threshold;
end

% for iter = 2 : size(trip,1) - 1
%     P1 = trip(iter-1,:);
%     P2 = trip(iter,:);
%     P3 = trip(iter+1,:);
%     angle = atan2(abs(det([P3 - P1 ; P2 - P1])), dot(P3 - P1, P2 - P1));
%     data = [data ; angle];
%     straight(iter) = angle <= threshold;
% end

% trip = rotate(trip);
h = figure;
hold on;

markers = '..';
colors = 'rg';
plot(trip(:,1), trip(:,2));
for iter = 0 :1
    xs = trip(straight == iter, 1);
    ys = trip(straight == iter, 2);
    
    plot(xs, ys, [markers(iter+1) colors(iter+1)], 'MarkerSize', 10);
end

saveas(h,'bochtjes','epsc')
saveas(h,'bochtjes','fig')

% h = figure;
% hold on;
% title('diff');
% 
% markers = '..';
% colors = 'rk';
% plot(trip(:,1), trip(:,2));
% for iter = 0 : 1
%     xs = trip(straight2 == iter, 1);
%     ys = trip(straight2 == iter, 2);
%     
%     plot(xs, ys, [markers(iter+1) colors(iter+1)], 'MarkerSize', 10);
% end
% 
% saveas(h,'bochtjes','epsc')
% saveas(h,'bochtjes','fig')

