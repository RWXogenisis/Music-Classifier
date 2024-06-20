import javax.swing.*;
import javax.swing.filechooser.FileNameExtensionFilter;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeModel;
import javax.swing.event.TreeSelectionEvent;
import javax.swing.event.TreeSelectionListener;
import java.awt.*;
import java.io.*;

public class final_page extends JFrame {

    private JTree fileTree;
    private JTextArea fileDetailsTextArea;
    private File sourceCodeFolder;

    public final_page() {
        setTitle("File Explorer");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setSize(600, 400);
        setLocationRelativeTo(null);

        sourceCodeFolder = new File(System.getProperty("user.dir"));

        File root = new File(System.getProperty("user.home"));
        DefaultMutableTreeNode rootNode = new DefaultMutableTreeNode(new FileNode(root));
        DefaultTreeModel treeModel = new DefaultTreeModel(rootNode);

        fileTree = new JTree(treeModel);
        fileTree.setRootVisible(false);
        fileTree.addTreeSelectionListener(new TreeSelectionListener() {
            public void valueChanged(TreeSelectionEvent event) {
                DefaultMutableTreeNode selectedNode = (DefaultMutableTreeNode) fileTree.getLastSelectedPathComponent();
                if (selectedNode != null) {
                    FileNode node = (FileNode) selectedNode.getUserObject();
                    File selectedFile = node.getFile();
                    displayFileDetails(selectedFile);
                }
            }
        });
        JScrollPane treeScrollPane = new JScrollPane(fileTree);

        fileDetailsTextArea = new JTextArea();
        fileDetailsTextArea.setEditable(false);
        JScrollPane detailsScrollPane = new JScrollPane(fileDetailsTextArea);

        JSplitPane splitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, treeScrollPane, detailsScrollPane);
        getContentPane().add(splitPane, BorderLayout.CENTER);

        openFileChooser();
    }

    private void displayFileDetails(File file) {
        StringBuilder details = new StringBuilder();
        if (file.isDirectory()) {
        } else {
            details.append("File: ").append(file.getAbsolutePath()).append("\n\n");
            String extension = getFileExtension(file);
            if (!"wav".equalsIgnoreCase(extension)) {
                details.append("Invalid file type. Only WAV files are supported.");
            } else {
                File destinationFile = new File(sourceCodeFolder, "temp.wav");
                if (destinationFile.exists()) {
                    if (destinationFile.delete()) {
                        details.append("Previous 'temp.wav' file deleted.\n");
                    } else {
                        details.append("Error deleting the existing 'temp.wav' file.\n");
                    }
                }

                try {
                    copyFile(file, destinationFile);
                    details.append("WAV file copied successfully to: ").append(destinationFile.getAbsolutePath());

                    Desktop.getDesktop().open(destinationFile);
                } catch (IOException e) {
                    details.append("Error copying file: ").append(e.getMessage());
                }
            }
        }
        fileDetailsTextArea.setText(details.toString());
    }
    private void copyFile(File source, File destination) throws IOException {
        try (InputStream in = new FileInputStream(source);
             OutputStream out = new FileOutputStream(destination)) {
            byte[] buffer = new byte[4096];
            int length;
            while ((length = in.read(buffer)) > 0) {
                out.write(buffer, 0, length);
            }
        }
    }

    private String getFileExtension(File file) {
        String extension = "";
        String fileName = file.getName();
        int dotIndex = fileName.lastIndexOf(".");
        if (dotIndex > 0 && dotIndex < fileName.length() - 1) {
            extension = fileName.substring(dotIndex + 1).toLowerCase();
        }
        return extension;
    }

    private void openFileChooser() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setFileSelectionMode(JFileChooser.FILES_ONLY);
        fileChooser.setFileFilter(new FileNameExtensionFilter("WAV Files", "wav"));

        int result = fileChooser.showOpenDialog(this);
        if (result == JFileChooser.APPROVE_OPTION) {
            File selectedFile = fileChooser.getSelectedFile();
            displayFileDetails(selectedFile);
        } else {
            System.exit(0);
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                new final_page().setVisible(true);
            }
        });
    }
}

class FileNode {
    private File file;

    public FileNode(File file) {
        this.file = file;
    }

    public File getFile() {
        return file;
    }

    public String toString() {
        return file.getName();
    }
}